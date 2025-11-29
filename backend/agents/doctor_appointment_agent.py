from typing import Literal, List, Any, Optional
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from prompt_library.doctor_appointment_prompt import supervisor_system_prompt, info_agent_system_prompt, booking_agent_prompt
from utils.llms import LLMModel
from toolkit.toolkits import *
from toolkit.toolkits import (
            # check_appointment_availability,
            check_availability_by_doctor,
            check_availability_by_specialization,
            # create_booking_request,
            # confirm_booking,
            # process_payment,
            set_appointment,
            cancel_appointment,
            reschedule_appointment,
        )

class Router(TypedDict):
    next: Literal[
        "information_node",
        "booking_node",
        "FINISH",
    ]
    reasoning: str
    instructions: str


class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    current_instructions: str
    steps_taken: int
    memory_context: str


class DoctorAppointmentAgent:
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()

    def _latest_user_query(self, messages: List[Any]) -> str:
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
        return ""

    def _format_recent_messages(self, messages: List[Any], limit: int = 6) -> str:
        if not messages:
            return "No prior conversation."

        window = messages[-limit:]
        formatted_blocks = []
        for msg in window:
            role = "User" if isinstance(msg, HumanMessage) else getattr(msg, "name", "Assistant")
            formatted_blocks.append(f"{role}: {msg.content}")
        return "\n".join(formatted_blocks)

    def supervisor_node(
        self, state: AgentState
    ) -> Command[
        Literal[
            "information_node",
            "booking_node",
            "__end__",
        ]
    ]:
        
        supervisor_system_prompt = (
            "You are the **Supervisor Agent** for a medical doctor-appointment assistant.\n"
            "Your job is NOT to talk to the user directly, but to **route** each turn to the correct specialist worker.\n\n"

            "### SPECIALIZED ASSISTANTS\n"
            "1. information_node\n"
            "   - Purpose: Answer questions about doctor availability, working hours, fees, and FAQs.\n"
            "   - Typical queries: 'What times is Dr. Sarah free on 18-12-2024?', "
            "'Which dentists are available tomorrow?', 'How much is a consultation?'\n\n"
            "2. booking_node\n"
            "   - Purpose: Create, confirm, cancel, or reschedule concrete appointments.\n"
            "   - Typical queries: 'Book me with Dr. Sarah at 10AM', "
            "'Cancel my appointment with Dr. John on 20-12-2024', "
            "'Reschedule my appointment from 18-12-2024 10:00 to 19-12-2024 11:00'.\n\n"

            "### YOUR GOAL\n"
            "- Shepherd medical-appointment requests end-to-end with **minimum back-and-forth**, but give the user the full information they need.\n"
            "- Reuse information the user already gave (doctor, date, time, ID) instead of asking again.\n"
            "- If the user's query is clearly answered, no further tool calls are needed, and there is no new question → respond with `FINISH`.\n"
            "- Use memory context, prior summaries, and current turns to decide what comes next.\n\n"

            "### ROUTING LOGIC\n"
            "- Route to **information_node** when the user is:\n"
            "  - Asking about availability, options, or general information.\n"
            "  - Unsure of doctor or time and needs suggestions.\n"
            "  - Asking 'who is free', 'what times are available', or similar.\n"
            "- Route to **booking_node** when the user:\n"
            "  - Clearly wants to **book, confirm, cancel, or reschedule** an appointment.\n"
            "  - Has already chosen a doctor and date/time (or most details), even if a few small details are missing.\n"
            "  - Is continuing a previous booking flow (e.g., confirming a booking reference, proceeding to payment).\n"
            "- Do **not** send the user back to information_node after booking_node has already obtained "
            "availability, unless the user explicitly asks a new information question.\n\n"

            "### WHEN TO USE FINISH\n"
            "- Use `FINISH` **only** when:\n"
            "  - The latest user message is clearly satisfied (e.g., 'Thanks', 'That’s all', 'Perfect, done'), OR\n"
            "  - You have answered to the user's query and there is no pending question, OR\n"
            "  - You have confirmed a booking/cancellation/reschedule and there is no pending question, OR\n"
            "  - Safety or policy issues require ending the flow.\n"
            "- Do **not** loop: if the same user request has been fully handled, choose `FINISH` instead of routing again.\n\n"

            "### MEMORY & CONTEXT\n"
            "- You may see a `memory_context` describing past visits or preferences. Use it to:\n"
            "  - Prefer the user’s usual doctor or time windows when that matches the current request.\n"
            "  - Avoid re-asking for ID or preference details already present in memory.\n"
            "- You may also see a message like 'Steps completed so far: N'. If N is high, prefer to **finish** rather than loop.\n\n"

            "### RESPONSE FORMAT (STRICT)\n"
            "Return a JSON object with exactly these keys:\n"
            '1. \"next\": one of [\"information_node\", \"booking_node\", \"FINISH\"].\n'
            "   - Choose the single best next step.\n"
            '2. \"reasoning\": 1–3 concise, high-level sentences explaining your choice.\n'
            "   - Do NOT reveal long step-by-step chain-of-thought; keep it short and outcome-focused.\n"
            '3. \"instructions\": clear directives for the selected worker.\n'
            "   - Include: which doctor/date/time/ID to rely on, which tools to call, and any constraints (e.g., "
            "'do not re-ask for patient ID, it is already known').\n\n"

            "### IMPORTANT RULES\n"
            "1. If the user's query is clearly answered, no further tool calls are needed, and there is no new question → respond with `FINISH`.\n"
            "2. If more than 10 total steps have occurred in this session, strongly prefer `FINISH` to prevent infinite recursion.\n"
            "3. Never ask the user for information that is already present in the conversation or memory_context.\n"
            "4. Always leverage prior memory context and tool outputs to avoid repeating work.\n"
            "5. If the intent mixes information + booking, prioritize the **action**: "
            "send to booking_node and let it call information tools if needed.\n"
        )

        supervisor_messages = [
            SystemMessage(content=supervisor_system_prompt),
            HumanMessage(
                content=(
                    f"User identification number is {state['id_number']}. "
                    f"Steps completed so far: {state.get('steps_taken', 0)}."
                )
            ),
        ]
        if state.get("memory_context"):
            supervisor_messages.append(
                SystemMessage(content=f"Persistent memory context:\n{state['memory_context']}")
            )

        supervisor_messages += state["messages"]

        latest_query = self._latest_user_query(state["messages"])

        response = self.llm_model.with_structured_output(Router).invoke(supervisor_messages)
        print("Doctor Appointment response: ", response)
        print("================================================")
        print("")

        goto_label = response["next"]
        goto = END if goto_label == "FINISH" else goto_label

        supervisor_summary = (
            f"Supervisor routed to {goto_label}. Reasoning: {response['reasoning']} "
            f"Instructions: {response['instructions']} "
        )
        print("Supervisor summary: ", supervisor_summary)
        print("================================================")
        print("")
        messages = state["messages"] + [AIMessage(content=supervisor_summary, name="supervisor")]
   
        update_payload = {
            "next": goto_label,
            "current_reasoning": response["reasoning"],
            "current_instructions": response["instructions"],
            "steps_taken": state.get("steps_taken", 0) + 1,
            "messages": messages,
        }
        print("Update payload: ", update_payload)
        print("Goto: ", goto)
        if latest_query:
            update_payload["query"] = latest_query

        return Command(goto=goto, update=update_payload)


    def information_node(self, state: AgentState) -> Command[Literal["supervisor"]]:

        info_agent_system_prompt =  (
            "You are the **Information Specialist** for DOCTOR APPOINTMENTS in a medical appointment orchestration team.\n"
            "You do NOT decide routing; your job is to answer information questions clearly and "
            "use tools to check real availability for doctors only.\n\n"

            "### DOMAIN SCOPE\n"
            "- You ONLY handle queries related to doctors and doctor appointments "
            "(availability, schedules, fees, basic doctor info).\n"
            "- You MUST NOT handle lab tests, diagnostics, lab reports, or lab bookings. "
            "Those are handled by a separate Lab & Diagnostics agent.\n"
            "- If the user asks about lab tests or diagnostics while you are active, "
            "politely say that lab-related questions are handled by a different assistant and "
            "stick to doctor-related information only.\n\n"

            "### CONTEXT FROM SUPERVISOR\n"
            f"- Supervisor reasoning:\n{state.get('current_reasoning', '')}\n\n"
            f"- Action plan:\n{state.get('current_instructions', '')}\n\n"
            f"- Long-term memory context:\n{state.get('memory_context', '')}\n\n"

            "### YOUR JOB\n"
            "- Use the approved tools to fetch **real** doctor availability and related information.\n"
            "- Prefer using details already mentioned by the user (doctor, specialization, date) "
            "instead of asking again.\n"
            "- If the user did not specify enough details to call a tool (e.g., no date), ask only "
            "for the **minimum required information**.\n\n"

            "### TOOL SELECTION\n"
            # "- Use `check_appointment_availability` when the user mentions a **specific doctor AND exact date+time**.\n"
            "- Use `check_availability_by_doctor` when the user mentions a **specific doctor and date**, "
            "but not a specific time.\n"
            "- Use `check_availability_by_specialization` when the user mentions a **specialization and date**, "
            "but not a specific doctor.\n\n"

            "### RESPONSE STYLE\n"
            "- First, summarize the key availability information in 1–2 short sentences.\n"
            "- Then, clearly suggest next steps (e.g., 'If you like, I can book one of these slots for you.').\n"
            "- If there is **no availability**, say that clearly and propose alternatives "
            "(e.g., another time on the same day, or suggest trying another doctor/specialization).\n"
            "- Do NOT invent times or availability if the tools return nothing.\n"
        )


        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", info_agent_system_prompt),
                ("placeholder", "{messages}"),
            ]
        )

        information_agent = create_react_agent(
            model=self.llm_model,
            tools=[
                check_availability_by_doctor, 
                check_availability_by_specialization
                ],
            prompt=prompt,
        )
        result = information_agent.invoke(state)
        print("Information agent result: ", result)
        print("Information agent goto: ", "supervisor")
        print("================================================")
        print("")
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="information_node")
                ]
            },
            goto="supervisor",
        )

    def booking_node(self, state: AgentState) -> Command[Literal["supervisor"]]:

        booking_agent_prompt = (
            f"""
            You are the Booking Specialist for a medical appointment system.

            Your job:
            - Create, cancel, or reschedule doctor appointments.
            - Use tools to read/write from the scheduling database.
            - Return one clear, final message to the user for this turn.

            Context from the supervisor:
            - Reasoning: {state.get('current_reasoning', '')}
            - Plan: {state.get('current_instructions', '')}

            Long-term memory (may or may not be relevant):
            {state.get('memory_context', '')}

            Guidelines:
            1. First, understand what the user wants (new booking vs cancel vs reschedule).
            2. Rely on details already in the conversation; 
            3. Never guess any database-backed fact (availability, status, etc.). Always call the appropriate tool instead.
            4. When you call tools, interpret their results and then explain to the user in simple language:
            - what you did,
            - what happened (success / failure),
            - what the next step is, if any.
            5. If the booking action is complete (booked / cancelled / rescheduled) and there is no new open question from the user, clearly confirm the outcome and avoid restarting a new booking flow.
            """
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", booking_agent_prompt),
                ("placeholder", "{messages}"),
            ]
        )
        
        booking_agent = create_react_agent(
            model=self.llm_model,
            tools=[
                set_appointment,  # Keep for backward compatibility
                cancel_appointment,
                reschedule_appointment,
            ],
            prompt=prompt,
        )
        result = booking_agent.invoke(state)
        print("Booking agent result: ", result)
        print("================================================")
        print("")
        # print("Booking agent goto: ", "supervisor")

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="booking_node")
                ]
            },
            goto="supervisor",
        )


    def workflow(self):
        self.graph = StateGraph(AgentState)
        self.graph.add_node("supervisor", self.supervisor_node)
        self.graph.add_node("information_node", self.information_node)
        self.graph.add_node("booking_node", self.booking_node)
        # self.graph.add_node("clarification_node", self.clarification_node)
        # self.graph.add_node("followup_node", self.followup_node)
        self.graph.add_edge(START, "supervisor")
        self.app = self.graph.compile()
        return self.app


