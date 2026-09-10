from agent import ask_agent

from memory import initialize_database

initialize_database()


USER_ID = "student_001"


print("Gemini Agent")
print("Type 'exit' to stop.")


while True:

    user_message = input("\nYou: ")


    if user_message.lower() == "exit":
        break


    response = ask_agent(
        USER_ID,
        user_message
    )


    print("\nAgent:", response)