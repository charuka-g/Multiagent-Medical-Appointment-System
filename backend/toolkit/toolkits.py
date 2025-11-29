from typing import Literal
from langchain_core.tools import tool
from data_models.models import *
from dotenv import load_dotenv
# import os
# import psycopg2
from datetime import datetime, timedelta
import uuid
from db.db_connection import connect_to_db
from utils.data_access import load_json_file


@tool
def check_availability_by_doctor(
    desired_date: DateModel,
    doctor_name: Literal[
        "lisa brown", "alexander turner", "sophia clark", "emily johnson", "olivia rodriguez", "matthew thompson", "daniel miller", "susan davis", "rebecca scott", "sarah wilson", "jennifer white", "nicholas adams", "laura mitchell", "michael green", "david lee", "amanda taylor", "ryan cooper", "kevin anderson", "christopher brown", "rachel moore", "kevin anderson", "jessica martinez", "daniel campbell", "ashley evans", "patricia davis", "robert stewart", "linda murphy", "william jones", "elizabeth taylor", "mark cook", "nancy thomas", "charles jackson", "paul rogers", "barbara harris", "sandra reed", "george howard", "margaret lewis", "carol torres", "kenneth peterson", "john doe"
    ]
):
    """
    Check the Supabase PostgreSQL doctor_appointments table to see
    if a doctor has available slots for a given date.
    """

    # Database connection
    conn = connect_to_db()
    cur = conn.cursor()

    # print(cur)

    # Query available slots with consultation fee
    query = """
        SELECT TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI') AS ts, consultation_fee
        FROM doctor_appointments
        WHERE doctor_name = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY') = %s
          AND is_available = TRUE
        ORDER BY TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI');
    """

    cur.execute(query, (doctor_name, desired_date.date))
    rows = cur.fetchall()
    # print("Fetched records: ", rows)

    # print(rows[0][0].strftime("%H:%M"))

    cur.close()
    conn.close()

    # Format response
    if not rows:
        return f"No availability for Dr. {doctor_name} on {desired_date.date}"

    # Extract time part (HH:MM) and consultation fee
    slots = [r[0].strftime("%H:%M") for r in rows]
    consultation_fee = rows[0][1] if rows else None

    output = f"Availability for Dr. {doctor_name} on {desired_date.date}:\n"
    output += ", ".join(slots)
    if consultation_fee:
        output += f"\nConsultation Fee: ${float(consultation_fee):.2f}"

    return output


@tool
def check_availability_by_specialization(
    desired_date: DateModel,
    specialization: Literal[
        "cardiology" , "dermatology", "neurology", "pediatrics", "emergency_medicine", "oral_surgeon", "orthodontist", "radiology", "surgery", "sport_medicine", "general_medicine", "hematalogists"
    ]
):
    """
    Check the Supabase PostgreSQL database for doctor availability
    filtered by specialization and date.
    """

    # Connect to DB
    conn = connect_to_db()
    cur = conn.cursor()

    # Query: Convert date_slot (text -> timestamp) and extract both date & time with consultation fee
    query = """
        SELECT 
            specialization,
            doctor_name,
            TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'HH24:MI') AS date_slot_time,
            consultation_fee
        FROM doctor_appointments
        WHERE specialization = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY') = %s
          AND is_available = TRUE
        ORDER BY doctor_name, TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI');
    """

    cur.execute(query, (specialization, desired_date.date))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Handle no availability
    if not rows:
        return f"No availability for {specialization.replace('_', ' ')} on {desired_date.date}"

    # Group by doctor_name → collect available times and consultation fee
    availability = {}
    doctor_fees = {}
    for specialization_, doctor_name, slot_time, consultation_fee in rows:
        availability.setdefault(doctor_name, []).append(slot_time)
        # Store consultation fee for each doctor (should be consistent per doctor)
        if doctor_name not in doctor_fees:
            doctor_fees[doctor_name] = consultation_fee

    # Convert to AM/PM format
    def convert_to_am_pm(time_str):
        hours, minutes = map(int, time_str.split(":"))
        period = "AM" if hours < 12 else "PM"
        hours = hours % 12 or 12
        return f"{hours}:{minutes:02d} {period}"

    # Build the output string
    output = f"This availability for {desired_date.date}\n"
    for doctor_name, slot_times in availability.items():
        am_pm_times = [convert_to_am_pm(t) for t in slot_times]
        fee = doctor_fees.get(doctor_name)
        fee_str = f" (Fee: ${float(fee):.2f})" if fee else ""
        output += f"{doctor_name}: Available slots → {', '.join(am_pm_times)}{fee_str}\n"

    return output


@tool
def set_appointment(
    desired_date: DateTimeModel,
    id_number: IdentificationNumberModel,
    doctor_name: Literal[
        "lisa brown", "alexander turner", "sophia clark", "emily johnson", "olivia rodriguez", "matthew thompson", "daniel miller", "susan davis", "rebecca scott", "sarah wilson", "jennifer white", "nicholas adams", "laura mitchell", "michael green", "david lee", "amanda taylor", "ryan cooper", "kevin anderson", "christopher brown", "rachel moore", "kevin anderson", "jessica martinez", "daniel campbell", "ashley evans", "patricia davis", "robert stewart", "linda murphy", "william jones", "elizabeth taylor", "mark cook", "nancy thomas", "charles jackson", "paul rogers", "barbara harris", "sandra reed", "george howard", "margaret lewis", "carol torres", "kenneth peterson", "john doe"
    ]
):
    """
    DEPRECATED: Use create_booking_request instead for new booking flow with confirmation and payment.
    Set appointment (book a slot) with the doctor in the Supabase PostgreSQL database.
    """

    conn = connect_to_db()
    cur = conn.cursor()

    # Step 1: Check if the given slot is available and get consultation fee
    check_query = """
        SELECT consultation_fee
        FROM doctor_appointments
        WHERE doctor_name = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
          AND is_available = TRUE;
    """

    cur.execute(check_query, (doctor_name, desired_date.date))
    available_slot = cur.fetchone()

    if not available_slot:
        cur.close()
        conn.close()
        return f"No available appointments for Dr. {doctor_name} at {desired_date.date}"

    consultation_fee = available_slot[0]

    # Step 2: Book (update) the appointment
    update_query = """
        UPDATE doctor_appointments
        SET is_available = FALSE,
            patient_to_attend = %s
        WHERE doctor_name = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
          AND is_available = TRUE;
    """

    cur.execute(update_query, (id_number.id, doctor_name, desired_date.date))
    conn.commit()  # Commit the update

    cur.close()
    conn.close()

    fee_str = f", Consultation Fee: ${float(consultation_fee):.2f}" if consultation_fee else ""
    return f"Successfully booked Dr. {doctor_name} for {desired_date.date} (Patient ID: {id_number.id}{fee_str})"


@tool
def cancel_appointment(
    date: DateTimeModel,
    id_number: IdentificationNumberModel,
    doctor_name: Literal[
        "lisa brown", "alexander turner", "sophia clark", "emily johnson", "olivia rodriguez", "matthew thompson", "daniel miller", "susan davis", "rebecca scott", "sarah wilson", "jennifer white", "nicholas adams", "laura mitchell", "michael green", "david lee", "amanda taylor", "ryan cooper", "kevin anderson", "christopher brown", "rachel moore", "kevin anderson", "jessica martinez", "daniel campbell", "ashley evans", "patricia davis", "robert stewart", "linda murphy", "william jones", "elizabeth taylor", "mark cook", "nancy thomas", "charles jackson", "paul rogers", "barbara harris", "sandra reed", "george howard", "margaret lewis", "carol torres", "kenneth peterson", "john doe"
    ]
):
    """
    Cancel an existing appointment in the Supabase PostgreSQL database.
    The parameters MUST be mentioned by the user in the query.
    """
    # 1️⃣ Connect to database
    conn = connect_to_db()
    cur = conn.cursor()

    # 2️⃣ Check if an appointment exists for the patient, doctor, and date
    check_query = """
        SELECT *
        FROM doctor_appointments
        WHERE doctor_name = %s
          AND patient_to_attend = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s;
    """

    cur.execute(check_query, (doctor_name, str(id_number.id), date.date))
    appointment = cur.fetchone()

    if not appointment:
        cur.close()
        conn.close()
        return f"No appointment found for Dr. {doctor_name} on {date.date} for patient ID {id_number.id}"

    # 3️⃣ Update the record to mark the slot available again
    update_query = """
        UPDATE doctor_appointments
        SET is_available = TRUE,
            patient_to_attend = NULL
        WHERE doctor_name = %s
          AND patient_to_attend = %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s;
    """

    cur.execute(update_query, (doctor_name, str(id_number.id), date.date))
    conn.commit()  # ✅ Commit the change

    cur.close()
    conn.close()

    return f"Successfully cancelled the appointment with Dr. {doctor_name} on {date.date} (Patient ID: {id_number.id})"

@tool
def reschedule_appointment(
    old_date: DateTimeModel,
    new_date: DateTimeModel,
    id_number: IdentificationNumberModel,
    doctor_name: Literal[
        "lisa brown", "alexander turner", "sophia clark", "emily johnson", "olivia rodriguez", "matthew thompson", "daniel miller", "susan davis", "rebecca scott", "sarah wilson", "jennifer white", "nicholas adams", "laura mitchell", "michael green", "david lee", "amanda taylor", "ryan cooper", "kevin anderson", "christopher brown", "rachel moore", "kevin anderson", "jessica martinez", "daniel campbell", "ashley evans", "patricia davis", "robert stewart", "linda murphy", "william jones", "elizabeth taylor", "mark cook", "nancy thomas", "charles jackson", "paul rogers", "barbara harris", "sandra reed", "george howard", "margaret lewis", "carol torres", "kenneth peterson", "john doe"
    ]
):
    """
    Reschedule an appointment in the Supabase PostgreSQL database.
    """

    conn = connect_to_db()

    try:
        with conn:  # ✅ psycopg2 will manage BEGIN / COMMIT / ROLLBACK automatically
            with conn.cursor() as cur:

                # 1️⃣ Check if the new slot is available and get consultation fee
                cur.execute("""
                    SELECT consultation_fee
                    FROM doctor_appointments
                    WHERE doctor_name = %s
                      AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
                      AND is_available = TRUE;
                """, (doctor_name, new_date.date))

                new_slot = cur.fetchone()
                if not new_slot:
                    return f"Not available slots for Dr. {doctor_name} at {new_date.date}"
                
                consultation_fee = new_slot[0]

                # 2️⃣ Cancel old appointment
                cur.execute("""
                    UPDATE doctor_appointments
                    SET is_available = TRUE,
                        patient_to_attend = NULL
                    WHERE doctor_name = %s
                      AND patient_to_attend::TEXT = %s
                      AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s;
                """, (doctor_name, str(id_number.id), old_date.date))

                # 3️⃣ Book new appointment
                cur.execute("""
                    UPDATE doctor_appointments
                    SET is_available = FALSE,
                        patient_to_attend = %s
                    WHERE doctor_name = %s
                      AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
                      AND is_available = TRUE;
                """, (str(id_number.id), doctor_name, new_date.date))

        conn.close()
        fee_str = f", Consultation Fee: ${float(consultation_fee):.2f}" if consultation_fee else ""
        return f"Successfully rescheduled appointment with Dr. {doctor_name} from {old_date.date} to {new_date.date} (Patient ID: {id_number.id}{fee_str})"

    except Exception as e:
        conn.close()
        return f"Error during rescheduling: {e}"


# Lab Test Tools


@tool
def check_lab_availability(
    desired_date: DateModel,
    test_name: Literal[
        "lipid panel", "complete blood count", "blood glucose test", "thyroid function test", "liver function test", "kidney function test", "Urine Analysis", "chest x-ray", "ecg", "vitamin d test"
        ]
):
    """
    Check available lab test slots for a given date. If test_name is provided, filters by that test.
    Returns available time slots.
    """
    conn = connect_to_db()
    cur = conn.cursor()

    if test_name:
        query = """
            SELECT test_name, TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'HH24:MI') AS time_slot, price
            FROM lab_tests
            WHERE test_name ILIKE %s
              AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY') = %s
              AND is_available = TRUE
            ORDER BY TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI');
        """
        cur.execute(query, (test_name, desired_date.date))
    else:
        query = """
            SELECT test_name, TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'HH24:MI') AS time_slot, price
            FROM lab_tests
            WHERE TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY') = %s
              AND is_available = TRUE
            ORDER BY test_name, TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI');
        """
        cur.execute(query, (desired_date.date,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return f"No available lab test slots on {desired_date.date}" + (f" for {test_name}" if test_name else "")

    # Group by test name
    availability = {}
    for test, time_slot, price in rows:
        if test not in availability:
            availability[test] = []
        availability[test].append((time_slot, float(price)))

    output = f"Available lab test slots on {desired_date.date}:\n"
    for test, slots in availability.items():
        slot_times = [f"{time} (${price:.2f})" for time, price in slots]
        output += f"{test}: {', '.join(slot_times)}\n"

    return output


@tool
def create_lab_booking_request(
    desired_date: DateTimeModel,
    id_number: IdentificationNumberModel,
    test_name: Literal[
        "lipid panel", "complete blood count", "blood glucose test", "thyroid function test", "liver function test", "kidney function test", "urine analysis", "chest x-ray", "ecg", "vitamin d test"
        ]
):
    """
    Create a booking request (pending confirmation) for a lab test.
    This creates a booking record that requires user confirmation before payment.
    """
    conn = connect_to_db()
    cur = conn.cursor()

    # Check availability
    check_query = """
        SELECT test_name, date_slot, price
        FROM lab_tests
        WHERE test_name ILIKE %s
          AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
          AND is_available = TRUE;
    """

    cur.execute(check_query, (test_name, desired_date.date))
    available_slot = cur.fetchone()

    if not available_slot:
        cur.close()
        conn.close()
        return f"BOOKING_UNAVAILABLE: No available slots for {test_name} at {desired_date.date}"

    test_name_db, date_slot, price = available_slot
    booking_ref = f"LAB-{uuid.uuid4().hex[:8].upper()}"

    update_query = """
        UPDATE lab_tests 
        SET is_available = FALSE,
            patient_to_attend = %s
        WHERE test_name ILIKE %s
        AND TO_CHAR(TO_TIMESTAMP(date_slot, 'DD-MM-YYYY HH24:MI'), 'DD-MM-YYYY HH24:MI') = %s
        AND is_available = TRUE;
    """

    cur.execute(update_query, (str(id_number.id), test_name_db, desired_date.date))
    
    conn.commit()

    cur.close()
    conn.close()

    return f"BOOKING_CREATED: Booking {booking_ref} created. Test: {test_name_db}, Date: {desired_date.date}, Amount: ${float(price):.2f}."  # Please confirm to proceed with payment.


@tool
def validate_test_prerequisites(
    test_name: Literal[
        "lipid panel", "complete blood count", "blood glucose test", "thyroid function test", "liver function test", "kidney function test", "Urine Analysis", "chest x-ray", "ecg", "vitamin d test"
        ],
    id_number: IdentificationNumberModel
):
    """
    Validate prerequisites for a lab test (e.g., fasting requirements, previous tests needed).
    """
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
        SELECT prerequisites
        FROM lab_tests
        WHERE test_name = %s
        LIMIT 1;
    """

    cur.execute(query, (test_name,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if not result:
        return f"Test {test_name} not found in the system."

    prerequisites = result[0] or "No specific prerequisites required."

    return f"Prerequisites for {test_name}:\n{prerequisites}\n\nPatient ID: {id_number.id}"