from typing import Literal
from langgraph.graph import START, StateGraph, END
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.llms import LLMModel
# from prompt_library.lab_test_prompt import lab_supervisor_prompt, lab_booking_agent_prompt, lab_info_prompt
from toolkit.toolkits import (
    check_lab_availability,
    create_lab_booking_request,
    validate_test_prerequisites,
    # track_test_status,
    # retrieve_lab_test_reports,
    # confirm_booking,
    # process_payment,
)


class LabRouter(TypedDict):
    next: Literal[
        "lab_booking_node",
        "lab_availability_and_info_node",
        "FINISH",
    ]
    reasoning: str
    instructions: str


class LabAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    current_instructions: str
    steps_taken: int
    memory_context: str


class LabAndDiagnosticsAgent:
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()

    def _latest_user_query(self, messages):
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
        return ""

    def supervisor_node(
        self, state: LabAgentState
    ) -> Command[
        Literal[
            "lab_booking_node",
            "lab_availability_and_info_node",
            "__end__",
        ]
    ]:
        # lab_supervisor_prompt = (
            # f"""
        #     You are the Lab and Diagnostics Supervisor Agent in a medical assistant system.

        #     Your job:
        #     - Understand the user's intent about lab tests.
        #     - Route the request to the correct sub-agent.
        #     - If the user's query is clearly answered, no further tool calls are needed, and there is no new question → respond with `FINISH`.
        #     - Decide when the lab flow is complete and should FINISH.

        #     Available sub-agents:
        #     - lab_booking_node: booking lab tests (creating booking requests).
        #     - lab_availability_and_info_node: checking lab availability, validating test prerequisites, and providing test information.
        #     - FINISH: use this when the user's request has been fully handled and there is no new open question.

        #     Routing rules:
        #     - If the user wants to book a test (create a booking request) → route to lab_booking_node.
        #     - If the user asks about available slots, test prerequisites, or general test information → route to lab_availability_and_info_node.
        #     - If all requested actions are completed and the user has no further question → choose FINISH.
        #     - Do NOT send the same request back and forth between nodes once it is resolved.

        #     Context:
        #     - User ID: {state['id_number']}
        #     - Steps completed so far: {state.get('steps_taken', 0)}

        #     Think step-by-step about the user's latest message and then choose exactly one next value: "lab_booking_node", "lab_availability_and_info_node", or "FINISH".
        #     """
        # )

        lab_supervisor_prompt = (
           f"""
            You are the **Lab & Diagnostics Supervisor Agent** in a medical assistant system.

            ### ROLE & SCOPE
            - You ONLY handle queries related to **lab tests and diagnostics**:
            - lab test bookings,
            - lab availability,
            - test prerequisites (e.g. fasting, medication restrictions),
            - lab test status and reports.
            - You MUST NOT handle doctor appointments or doctor availability. Those are handled by a separate doctor supervisor.

            ### YOUR JOB
            - Understand the user's current intent about lab tests.
            - Route the request to exactly one sub-agent per turn.
            - Decide when the overall lab flow is complete and should FINISH.
            - Avoid unnecessary back-and-forth once a request has been resolved.

            ### INFORMATION USAGE RULES
            - The patient ID for this conversation is always the `id_number` from context:
            - **Always treat `id_number` as the patient_id when calling tools.**
            - Do NOT ask the user to repeat or re-enter their patient ID.
            - If the conversation or memory already contains required details (e.g. test name, date, time, booking reference),
            you MUST reuse those values instead of asking again.
            - Only ask the user for **additional information** when it is absolutely required to call a tool and is not present
            in the current messages or memory_context.

            ### AVAILABLE SUB-AGENTS
            - **lab_booking_node**
            - Use when the user wants to create, confirm, or modify a **lab test booking**.
            - Typical intents: "book a blood test", "schedule an X test tomorrow", "change my lab test time".
            - **lab_availability_and_info_node**
            - Use when the user is asking about **available slots**, **test prerequisites**, or **general lab test information**.
            - Typical intents: "what time slots are available?", "do I need to fast?", "what tests are available on Friday?".
            - **FINISH**
            - Use when the user's request has been fully handled, and there is **no new open question**.
            - Also use if the user clearly indicates they are done (e.g. "thanks, that's all").

            ### ROUTING RULES
            - If the user wants to **book or change** a lab test → route to `lab_booking_node`.
            - If the user wants **availability, prerequisites, or general information** about lab tests → route to `lab_availability_and_info_node`.
            - If all requested actions are complete and there is no follow-up question → choose `FINISH`.
            - Do NOT bounce the same request repeatedly between the same nodes. Once a node has produced a clear answer and there is no new question, prefer `FINISH`.

            ### CONTEXT
            - User ID (patient_id): {state['id_number']}
            - Steps completed so far: {state.get('steps_taken', 0)}
            - If steps_completed is high and the same request has already been answered, prefer `FINISH` to avoid loops.

            ### OUTPUT FORMAT
            Think briefly about the latest user message and the conversation so far, then respond with a **single choice** for the `"next"` value:
            - `"lab_booking_node"`
            - `"lab_availability_and_info_node"`
            - `"FINISH"`
            """
        )

        
        if state.get("memory_context"):
            lab_supervisor_prompt += f"\nMemory context:\n{state['memory_context']}\n"

        supervisor_messages = [
            SystemMessage(content=lab_supervisor_prompt),
        ] + state["messages"]

        latest_query = self._latest_user_query(state["messages"])
        response = self.llm_model.with_structured_output(LabRouter).invoke(supervisor_messages)
        print("Lab and Diagnostics Supervisor response: ", response)
        print("================================================")
        print("")
        
        goto_label = response["next"]
        goto = "__end__" if goto_label == "FINISH" else goto_label

        supervisor_summary = (
            f"Lab Supervisor routed to {goto_label}. Reasoning: {response['reasoning']} "
            f"Instructions: {response['instructions']}"
        )

        messages = state["messages"] + [AIMessage(content=supervisor_summary, name="lab_supervisor")]

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
    

    def lab_booking_node(self, state: LabAgentState) -> Command[Literal["supervisor"]]:

        lab_booking_agent_prompt = (
            f"""
            You are the Lab Booking Specialist in a medical assistant system.

            Your job:
            - Create booking requests for lab tests that the user wants to book.
            - Only create bookings when the user has confirmed they want to book a specific test at a specific time.

            Context from the lab supervisor:
            - Reasoning: {state.get('current_reasoning', '')}
            - Plan: {state.get('current_instructions', '')}

            Long-term memory (may or may not be relevant):
            {state.get('memory_context', '')}

            Available tools:
            - create_lab_booking_request: create a lab booking request for a specific test, date/time, and patient.

            Guidelines:
            1. Only call create_lab_booking_request when the user has explicitly confirmed they want to book a test.
            2. Before creating a booking, ensure you have:
            - test_name,
            - desired date/time,
            - patient ID.
            3. If any information is missing, ask the user for clarification.
            4. After creating a booking, explain clearly:
            - what was booked,
            - the booking reference,
            - next steps (e.g., confirmation, payment).
            5. If the user's booking request has been fully handled and there is no new open question,
            give a clear confirmation and avoid starting a new booking flow.
            """
        )


        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", lab_booking_agent_prompt),
                ("placeholder", "{messages}"),
            ]
        )

        booking_agent = create_react_agent(
            model=self.llm_model,
            tools=[
                create_lab_booking_request,
                # confirm_booking,
                # process_payment,
            ],
            prompt=prompt,
        )
        result = booking_agent.invoke(state)
        print("Lab Booking agent result: ", result)
        print("================================================")
        print("")
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="lab_booking_node")
                ]
            },
            goto="supervisor",
        )

    def lab_availability_and_info_node(self, state: LabAgentState) -> Command[Literal["supervisor"]]:
        lab_availability_and_info_prompt = (
            f"""
            You are the Lab Availability and Information Specialist in a medical assistant system.

            Your job:
            - Check lab test availability for specific dates and tests.
            - Answer user questions about lab tests.
            - Provide prerequisites/requirements for tests.
            - (Optionally, track status or retrieve reports when those tools are enabled.)

            Context from the lab supervisor:
            - Reasoning: {state.get('current_reasoning', '')}
            - Plan: {state.get('current_instructions', '')}

            Long-term memory (may or may not be relevant):
            {state.get('memory_context', '')}

            Available tools:
            - check_lab_availability: find available lab test slots for a given date (optionally filtered by test name).
            - validate_test_prerequisites: return prerequisites or requirements for a specific test.

            Guidelines:
            1. Understand the user's question first:
            - Are they asking about available time slots for a test? → Use check_lab_availability.
            - Are they asking about how to prepare for a test or prerequisites? → Use validate_test_prerequisites.
            - Are they asking about status or reports? (If status/report tools are not available, say so calmly.)
            2. Use check_lab_availability to find real availability. Never guess available slots.
            3. Use validate_test_prerequisites whenever the user asks how to prepare or what is required for a test.
            4. Do not invent medical requirements; always rely on tool output for prerequisites.
            5. Answer in simple, clear language, and structure the response so the user knows:
            - what information you found,
            - what the user should know (availability, prerequisites, etc.),
            - any follow-up actions (e.g., "Please confirm if you want to book this test now.").
            6. If the question has been fully answered and there is no new follow-up request,
            end with a concise confirmation instead of starting a new flow.
            """
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", lab_availability_and_info_prompt),
                ("placeholder", "{messages}"),
            ]
        )

        info_agent = create_react_agent(
            model=self.llm_model,
            tools=[
                check_lab_availability,
                validate_test_prerequisites,
                # track_test_status,
                # retrieve_lab_test_reports,
            ],
            prompt=prompt,
        )
        result = info_agent.invoke(state)
        print("Lab Availability and Information agent result: ", result)
        print("================================================")
        print("")

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="lab_availability_and_info_node")
                ]
            },
            goto="supervisor",
        )

    def workflow(self):

        graph = StateGraph(LabAgentState)
        graph.add_node("supervisor", self.supervisor_node)
        graph.add_node("lab_booking_node", self.lab_booking_node)
        graph.add_node("lab_availability_and_info_node", self.lab_availability_and_info_node)
        graph.add_edge(START, "supervisor")
        app = graph.compile()
        return app

