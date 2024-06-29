import datetime

from bupa import fetch_appointments, logger, login, modify_appointment
from config import on_earliest_appointment_found, user


def main():
    try:
        root, resp = login(user)
    except Exception as e:
        logger.error("Failed to login: %s", e)
        exit(1)

    root, resp = modify_appointment(root, resp)
    curr, appointments = fetch_appointments(root, resp)

    logger.info("Current appointment: %s", curr)
    logger.info("Available appointments: %s", appointments)

    if not appointments:
        logger.info("No appointments available")
        return

    earliest_appointment: datetime.datetime = min(
        appointments, key=lambda x: abs(x - curr)
    )
    logger.info("Earliest appointment: %s", earliest_appointment)

    earliest_date = earliest_appointment.date()
    current_date = curr.date()

    if earliest_date > current_date:
        logger.info("Earliest appointment is after current appointment, skipping")
    elif earliest_date == current_date:
        logger.info("Earliest appointment is same as current appointment, skipping")
    else:
        logger.info("Earliest appointment is before current appointment, booking")
        on_earliest_appointment_found(earliest_appointment)


if __name__ == "__main__":
    main()
