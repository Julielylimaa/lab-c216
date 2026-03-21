import re
import sys

VALID_COURSES = frozenset({"GES", "GEC", "GET", "GEP"})
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

students = []
enrollment_counters = {}


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email.strip()))


def is_valid_course(course):
    return course.strip().upper() in VALID_COURSES


def generate_enrollment_id(course):
    course = course.strip().upper()
    if course not in enrollment_counters:
        enrollment_counters[course] = 0
    enrollment_counters[course] += 1
    return f"{course}{enrollment_counters[course]}"


def index_by_enrollment_id(enrollment_id):
    enrollment_id = enrollment_id.strip().upper()
    for i, s in enumerate(students):
        if s["enrollment_id"] == enrollment_id:
            return i
    return -1


def register_student():
    name = input("Name: ").strip()
    if not name:
        print("Invalid name.")
        return
    email = input("Email: ").strip()
    if not email or not is_valid_email(email):
        print("Invalid email. Use a valid address (e.g. name@domain.com).")
        return
    course = input("Course (e.g. GES, GEC, GET, GEP): ").strip().upper()
    if not is_valid_course(course):
        print(
            "Invalid course. Must be one of: "
            + ", ".join(sorted(VALID_COURSES))
            + "."
        )
        return
    enrollment_id = generate_enrollment_id(course)
    students.append(
        {
            "name": name,
            "email": email,
            "course": course,
            "enrollment_id": enrollment_id,
        }
    )
    print(f"Student registered. Enrollment ID: {enrollment_id}")


def list_students():
    if not students:
        print("No students registered.")
        return
    for s in students:
        print(
            f"{s['enrollment_id']} | {s['name']} | {s['email']} | {s['course']}"
        )


def update_student():
    enrollment_id = input("Student enrollment ID: ").strip()
    i = index_by_enrollment_id(enrollment_id)
    if i < 0:
        print("Student not found.")
        return
    s = students[i]
    name = input(f"Name [{s['name']}]: ").strip()
    email = input(f"Email [{s['email']}]: ").strip()
    course = input(f"Course [{s['course']}]: ").strip().upper()
    if email and not is_valid_email(email):
        print("Invalid email. Use a valid address (e.g. name@domain.com).")
        return
    if course and course != s["course"] and not is_valid_course(course):
        print(
            "Invalid course. Must be one of: "
            + ", ".join(sorted(VALID_COURSES))
            + "."
        )
        return
    if name:
        s["name"] = name
    if email:
        s["email"] = email
    if course and course != s["course"]:
        new_id = generate_enrollment_id(course)
        s["course"] = course
        s["enrollment_id"] = new_id
        print(f"Course changed. New enrollment ID: {new_id}")
    else:
        print("Record updated.")


def remove_student():
    enrollment_id = input("Student enrollment ID: ").strip()
    i = index_by_enrollment_id(enrollment_id)
    if i < 0:
        print("Student not found.")
        return
    removed = students.pop(i)
    print(f"Removed: {removed['enrollment_id']} - {removed['name']}")


def display_menu():
    print()
    print("1 - Register student")
    print("2 - List students")
    print("3 - Update student")
    print("4 - Remove student")
    print("0 - Exit")


def main():
    while True:
        display_menu()
        choice = input("Option: ").strip()
        if choice == "1":
            register_student()
        elif choice == "2":
            list_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            remove_student()
        elif choice == "0":
            sys.exit(0)
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
