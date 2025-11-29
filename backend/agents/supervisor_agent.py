from typing import Literal
from langgraph.types import Command
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph, END
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.llms import LLMModel
from agents.doctor_appointment_agent import DoctorAppointmentAgent
from agents.lab_agent import LabAndDiagnosticsAgent


class TopLevelRouter(TypedDict):
    next: Literal[
        "doctor_appointment_agent",
        "lab_diagnostics_agent",
        "FINISH",
    ]
    reasoning: str
    instructions: str


class SupervisorAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    current_instructions: str
    steps_taken: int
    memory_context: str


class SupervisorAgent:
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()
        self.doctor_agent = DoctorAppointmentAgent()
        self.lab_agent = LabAndDiagnosticsAgent()

    def _latest_user_query(self, messages):
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
        return ""

    def supervisor_node(
        self, state: SupervisorAgentState
    ) -> Command[
        Literal[
            "doctor_appointment_agent",
            "lab_diagnostics_agent",
            "__end__",
        ]
    ]:
        # Check if inner agents have already provided final answers
        has_final_answer = False
        final_answer_content = None
        
        # Look for agent node responses in recent messages
        agent_node_names = ["information_node", "booking_node", "lab_booking_node", "lab_availability_and_info_node", "closing", "final_response"]

        for msg in reversed(state.get("messages", [])):
            if hasattr(msg, 'name') and msg.name in agent_node_names:
                has_final_answer = True
                final_answer_content = msg.content
                break
        
        # Check if inner agent marked as finished
        if state.get("next") == "FINISH":
            has_final_answer = True

        supervisor_prompt = (
            "You are the Top-Level Supervisor Agent for a medical appointment system. "
            "Route user requests to the appropriate specialized agent:\n\n"
            "### AGENTS:\n"
            "1. doctor_appointment_agent: Handles doctor appointments, availability checks of the doctors, booking, cancellation, rescheduling for doctors, and all related queries to doctors\n"
            "2. lab_diagnostics_agent: Handles lab tests, test booking, test status tracking, test reports, prerequisites validation, and all related queries to lab tests and diagnostics\n"
            "3. FINISH: When the task is complete and user is satisfied\n\n"
            "**CRITICAL ROUTING RULES:**\n"
            f"- Steps completed: {state.get('steps_taken', 0)}. Maximum allowed: 20 steps.\n"
            "- If steps_taken >= 10, you MUST route to FINISH to prevent infinite loops.\n"
            f"- IMPORTANT: {'A specialized agent has already provided a final answer. You MUST route to FINISH immediately.' if has_final_answer else 'If the user\'s query has been fully answered, route to FINISH immediately.'}\n"
            # "- If you've already routed to the same agent 3+ times for the same query, route to FINISH.\n"
            "- If a specialized agent has already given a clear final answer (check for messages from information_node, booking_node, lab_booking_node, lab_availability_and_info_node, or closing), you MUST choose FINISH.\n"
            # "- Do NOT route back to the same agent again for the same user query.\n"
            "- If the task is complete, route to FINISH\n\n"
            "- If the user asks about doctors, appointments for doctors, doctors availability, doctors consultations → route to doctor_appointment_agent\n"
            "- If the user asks about lab tests, diagnostics, test results, or test booking → route to lab_diagnostics_agent\n"
            "- If the query is ambiguous, ask user to provide more information\n"
            "- If the task is complete, route to FINISH\n\n"
            f"User ID: {state['id_number']}\n"
            f"Steps completed: {state.get('steps_taken', 0)}\n"
        )
        
        if has_final_answer and final_answer_content:
            supervisor_prompt += f"\n**CURRENT STATUS:** A specialized agent has already provided this final answer: {final_answer_content[:200]}... You MUST route to FINISH now.\n"
        
        if state.get("memory_context"):
            supervisor_prompt += f"\nMemory context:\n{state['memory_context']}\n"

        supervisor_messages = [
            SystemMessage(content=supervisor_prompt),
        ] + state["messages"]

        latest_query = self._latest_user_query(state["messages"])

        response = self.llm_model.with_structured_output(TopLevelRouter).invoke(supervisor_messages)
        print("Supervisor response: ", response)

        print("================================================")
        print("")
        
        goto_label = response["next"]
        goto = "__end__" if goto_label == "FINISH" else goto_label

        supervisor_summary = (
            f"Supervisor routed to {goto_label}. Reasoning: {response['reasoning']} "
            f"Instructions: {response['instructions']}"
        )

        messages = state["messages"] + [AIMessage(content=supervisor_summary, name="top_supervisor")]
        
        # If finishing, ensure we have the final answer from inner agents
        if goto_label == "FINISH":
            # Extract final answer from agent responses
            final_answer = self._extract_final_answer(state.get("messages", []))
            
            if final_answer:
                # Use the actual agent response as the final message
                messages.append(
                    AIMessage(
                        content=final_answer,
                        name="final_response",
                    )
                )
            else:
                # Fallback if no answer found
                messages.append(
                    AIMessage(
                        content="We're not able to assist you now with your query, please contact +94773531234. Have a great day!",
                        name="closing",
                    )
                )

        update_payload = {
            "next": goto_label,
            "current_reasoning": response["reasoning"],
            "current_instructions": response["instructions"],
            "steps_taken": state.get("steps_taken", 0) + 1,
            "messages": messages,
        }
        print("Update payload: ", update_payload)
        print("Goto: ", goto)
        print("================================================")
        print("")
        
        if latest_query:
            update_payload["query"] = latest_query

        return Command(goto=goto, update=update_payload)

    def _extract_final_answer(self, messages):
        """Extract the final meaningful answer from agent messages"""
        # Look for the last meaningful response from agent nodes
        agent_node_names = ["information_node", "booking_node", "lab_booking_node", "lab_availability_and_info_node", "closing"]
        
        # Find the last message from an agent node
        for msg in reversed(messages):
            if hasattr(msg, 'name') and msg.name in agent_node_names:
                return msg.content
        
        # If no agent node message found, get the last AI message
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and hasattr(msg, 'content'):
                # Skip supervisor routing messages
                if hasattr(msg, 'name') and msg.name in ["supervisor", "top_supervisor", "lab_supervisor"]:
                    continue
                return msg.content
        
        return None

    def doctor_appointment_agent_node(self, state: SupervisorAgentState) -> Command[Literal["supervisor", "__end__"]]:
        """Delegate to Doctor Appointment Agent"""
        # Convert state to DoctorAppointmentAgent format
        doctor_state = {
            "messages": state["messages"],
            "id_number": state["id_number"],
            "next": "",
            "query": state.get("query", ""),
            "current_reasoning": state.get("current_reasoning", ""),
            "current_instructions": state.get("current_instructions", ""),
            "steps_taken": state.get("steps_taken", 0),
            "memory_context": state.get("memory_context", ""),
        }

        app_graph = self.doctor_agent.workflow()
        result = app_graph.invoke(doctor_state, config={"recursion_limit": 20})

        inner_next = result.get("next")
        
        # Check if inner agent has finished
        if inner_next == "FINISH" or inner_next == "__end__":
            # Inner agent has completed - extract final answer and end
            final_answer = self._extract_final_answer(result["messages"])
            
            # Update messages with final answer if we found one
            updated_messages = result["messages"]
            if final_answer:
                # Ensure the final answer is the last message
                updated_messages = result["messages"] + [
                    AIMessage(content=final_answer, name="final_response")
                ]
            
            return Command(
                update={
                    "messages": updated_messages,
                    "steps_taken": result.get("steps_taken", state.get("steps_taken", 0)),
                    "next": "FINISH",  # Mark as finished
                },
                goto="__end__",
            )
        else:
            # Inner agent needs more processing - go back to supervisor
            return Command(
                update={
                    "messages": result["messages"],
                    "steps_taken": result.get("steps_taken", state.get("steps_taken", 0)),
                },
                goto="supervisor",
            )

    def lab_diagnostics_agent_node(self, state: SupervisorAgentState) -> Command[Literal["supervisor", "__end__"]]:
        """Delegate to Lab and Diagnostics Agent"""
        # Convert state to LabAgentState format
        lab_state = {
            "messages": state["messages"],
            "id_number": state["id_number"],
            "next": "",
            "query": state.get("query", ""),
            "current_reasoning": state.get("current_reasoning", ""),
            "current_instructions": state.get("current_instructions", ""),
            "steps_taken": state.get("steps_taken", 0),
            "memory_context": state.get("memory_context", ""),
        }

        app_graph = self.lab_agent.workflow()
        result = app_graph.invoke(lab_state, config={"recursion_limit": 20})

        inner_next = result.get("next")

        # Check if inner agent has finished
        if inner_next == "FINISH" or inner_next == "__end__":
            # Inner agent has completed - extract final answer and end
            final_answer = self._extract_final_answer(result["messages"])
            
            # Update messages with final answer if we found one
            updated_messages = result["messages"]
            if final_answer:
                # Ensure the final answer is the last message
                updated_messages = result["messages"] + [
                    AIMessage(content=final_answer, name="final_response")
                ]
            
            return Command(
                update={
                    "messages": updated_messages,
                    "steps_taken": result.get("steps_taken", state.get("steps_taken", 0)),
                    "next": "FINISH",  # Mark as finished
                },
                goto="__end__",
            )
        else:
            # Inner agent needs more processing - go back to supervisor
            return Command(
                update={
                    "messages": result["messages"],
                    "steps_taken": result.get("steps_taken", state.get("steps_taken", 0)),
                },
                goto="supervisor",
            )

    def workflow(self):

        graph = StateGraph(SupervisorAgentState)
        graph.add_node("supervisor", self.supervisor_node)
        graph.add_node("doctor_appointment_agent", self.doctor_appointment_agent_node)
        graph.add_node("lab_diagnostics_agent", self.lab_diagnostics_agent_node)
        graph.add_edge(START, "supervisor")
        app = graph.compile()
        return app

