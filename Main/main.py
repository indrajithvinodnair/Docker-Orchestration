from dockerOperations import dockerOps
def printOpts():
    print("Menu of actions:")
    print("1. List all containers")
    print("2. List all stopped/exited containers")
    print("3. List all running containers")
    print("4. Run a container")
    print("5. Execute a Command on a container")
    print("6. Remove a container")
    print("7. Stop and Remove all containers")
    print("8. create a docker file, deploy it to EC2 and print output")
    print("9. Run Docker compose operation")
    print("Enter quit to Exit the program")

docker = dockerOps()
choice="quit"
while(choice!="quite"):
    printOpts()
    choice=input("Enter your choice: ")
    if(choice=="1"):
        docker.getContainers(None,False)
    elif(choice=="2"):
        docker.getContainers("exited",False)
    elif(choice=="3"):
        docker.getContainers("running",False)
    elif(choice=="4"):
        docker.runContainer()
    elif(choice=="5"):
        docker.runCommand()
    elif(choice=="6"):
        docker.removeContainer()
    elif(choice=="7"):
        docker.stopRemoveAllContainers()
    elif(choice=="8"):
        docker.deployToEC2()
    elif(choice=="9"):
        docker.runDockerCompose()
    elif(choice=="quit"):
        print("Exiting the program")
        break
    else:
        print("Invalid choice, please enter a valid choice")

