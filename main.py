from agents import aws_agent

if __name__ == "__main__":
    print("Jarvis AWS Agent Test")
    print("----------------------")
    result = aws_agent.list_ec2_instances()
    for r in result:
        print(r)
