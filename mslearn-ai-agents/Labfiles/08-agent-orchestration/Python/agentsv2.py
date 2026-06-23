# Add references
import os
import asyncio
from dotenv import load_dotenv
from agent_framework.foundry import FoundryChatClient as AzureAIAgentClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential
load_dotenv()

async def main():
    # Agent instructions
    summarizer_instructions = """
    Summarize the customer's feedback in one short sentence. Keep it neutral and concise.
    Example output:
    App crashes during photo upload.
    User praises dark mode feature.
    """
    classifier_instructions = """
    Classify the feedback as one of the following: Positive, Negative, or Feature request.
    """
    action_instructions = """
    Based on the summary and classification, suggest the next action in one short sentence.
    Example output:
    Escalate as a high-priority bug for the mobile team.
    Log as positive feedback to share with design and marketing.
    Log as enhancement request for product backlog.
    """
    # Create the chat client
    credential = AzureCliCredential()
    chat_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    )

    # Create agents
    summarizer = chat_client.as_agent(
        instructions=summarizer_instructions,
        name="summarizer",
    )
    classifier = chat_client.as_agent(
        instructions=classifier_instructions,
        name="classifier",
    )
    action = chat_client.as_agent(
        instructions=action_instructions,
        name="action",
    )
    # Initialize the current feedback
    feedback = """
    I use the dashboard every day to monitor metrics, and it works well overall. 
    But when I'm working late at night, the bright screen is really harsh on my eyes. 
    If you added a dark mode option, it would make the experience much more comfortable.
    """
    # Build sequential orchestration
    workflow = SequentialBuilder(participants=[summarizer, classifier, action]).build()

    # Run and collect outputs
    agent_outputs: list = [("user", f"Customer feedback:\n    {feedback.strip()}")]
    result = await workflow.run(f"Customer feedback: {feedback}", stream=False)

    for event in result:
        if event.type == "executor_completed" and isinstance(event.data, list):
            for item in event.data:
                if hasattr(item, 'executor_id') and hasattr(item, 'agent_response'):
                    text = getattr(item.agent_response, 'text', None)
                    if text:
                        agent_outputs.append((item.executor_id, text))

    # Display outputs
    for i, (agent_name, text) in enumerate(agent_outputs, start=1):
        print(f"{'-' * 60}\n{i:02d} [{agent_name}]\n{text}")

if __name__ == "__main__":
    asyncio.run(main())