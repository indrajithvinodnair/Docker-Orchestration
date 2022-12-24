import boto3
import docker
import paramiko
import pprint
from colorama import Fore, Style
import configparser
from Files.createDockerFile import fileOps


class dockerOps:
    def __init__(self):
        try:
            self.config = configparser.ConfigParser()
            self.config.read("config.ini")
            self.ec2= docker.DockerClient(base_url=self.config['CREDENTIALS']['url_base'])
        except Exception as e:
            print(e)
            print(Fore.RED+"Unable to connect to the remote instance")
            print(Style.RESET_ALL)
            exit()
            


    def getContainers(self,str,flag):
        if(str=="running"):
            print(Fore.YELLOW+"list of all running containers")
            containers = self.ec2.containers.list(all=True,filters={"status":"running"})
        elif(str=="exited"):
            print(Fore.RED+"list of all exited containers")
            containers = self.ec2.containers.list(all=True,filters={"status":"exited"})
        elif(str==None):
            print( Fore.GREEN+"list of all containers")
            containers = self.ec2.containers.list(all=True)
        
        self.listContainers(containers)
        print(Style.RESET_ALL)
        if(flag==True):
            return containers
    
    def listContainers(self,containers):
        print(Style.RESET_ALL)
        if(len(containers)==0):
            print(Fore.RED+" *****************     No containers such are present on the remote instance *************")
            print(Style.RESET_ALL)
        else:
            for container in containers:
                pprint.pprint(f'Name: {container.name}, Status: {container.status},  Image: {container.image.tags}, Id:{container.id}')
                print("--------------------------------------------------")

      

    def runContainer(self):
        containers = self.getContainers(None,True)
        if containers:
            try:
                imagename=input(Fore.GREEN+"Enter the name of the image (string present inside Imaage: [ ] is required ) to run: ")
                container=self.ec2.containers.run(imagename,detach=True)
                output = container.logs()
                print(Fore.YELLOW+"")
                print(output.decode('utf-8'))
                print(Style.RESET_ALL)
            except Exception as e:
                print(Style.RESET_ALL)
                print(e)
        else:
            print(Fore.RED+"No containers are present on the remote instance")
            print(Style.RESET_ALL)


    def runCommand(self):
        containers = self.getContainers("running",True)
        if len(containers)!=0:
            try:
                imagename=input(Fore.GREEN+"Enter the name of the image (Name : ) to run: ")
                command=input("Enter the command to run: ")
                container = self.ec2.containers.get(imagename)
                response = container.exec_run(command,stdout=True,
                                  stderr=True,
                                  stream=True)
                for chunk in response.output:
                    # Decode the chunk and print it
                    print(chunk.decode('utf-8'))

            except Exception as e:
                print(e)
                print(Fore.RED+"-----------    No such container is present on the remote instance ----------------")
                print(Style.RESET_ALL)
        else:
            print(Fore.RED+"--------------- No actively running containers are present on the remote instance ----------------")
            print(Style.RESET_ALL)


    def stopRemoveAllContainers(self):
       containers = self.getContainers(None,True)
       removed=[]
       for container in containers:
        container.stop()
        print("********************** "+container.name+"  has been stopped **********************")
        response=container.remove(force=True)
        removed.append(response)

       if len(removed)!=0:
        print(Fore.YELLOW+"All the containers have been removed")
        for i in removed:
            pprint.pprint(i)
            print("--------------------------------------------------")
        print(Style.RESET_ALL)
    

    def deployToEC2(self):
        try:
            client=docker.from_env()
            # username and password of dockerhub
            print(Fore.YELLOW+"*********** Pushing image to dockerhub  ****************")
            client.login(username=self.config['CREDENTIALS']['username_dockerHub'], password=self.config['CREDENTIALS']['password_docker_Hub'])
            dockerfileops = fileOps()
            dockerfileops.getSourceFile()
            dockerfileops.createDockerFile()
            dockerfileops.createDockerImage()

            image_name = dockerfileops.getimagename()
            client.images.get(image_name).tag(image_name)
            client.images.push(image_name)
            print(Fore.YELLOW+"**************** image pushed to dockerhub ****************")
            print(Fore.YELLOW+"**************** Retrviving image from dockerhub on the EC2 instance  **************")
            self.ec2.login(username=self.config['CREDENTIALS']['username_dockerHub'],password=self.config['CREDENTIALS']['password_docker_Hub'])
            print(Style.RESET_ALL)
            self.ec2.images.pull(image_name)
            response=self.ec2.containers.run(image_name, detach=True,stdout=True, stderr=True, stream=True)
            output = response.logs()
            output.decode("utf-8")
            print(Fore.GREEN+"**************** Imaged pulled from docker hub to EC2 instance , run image with option 4 from main menu  **************")
            print(Style.RESET_ALL)
        except Exception as e:
            print(e)
            print(Style.RESET_ALL)


    def removeContainer(self):
        containers = self.getContainers(None,True)
        if len(containers)!=0:
            try:
                imagename=input(Fore.GREEN+"Enter the name of the image (string present inside Image: [ ] is required ) to remove: ")
                container = self.ec2.containers.get(imagename)
                response= container.remove(force=True, v=True)
                print(Fore.YELLOW+"*************  Details of the container that has been now removed ****************")
                print(response)
                print(Style.RESET_ALL)
            except Exception as e:
                print(e)
                print(Fore.RED+"**************** No such container is present on the remote instance *****************")
                print(Style.RESET_ALL)
        else:
            print(Fore.RED+"***************** No containers are present on the remote instance *****************")
            print(Style.RESET_ALL)


    def runDockerCompose(self):
        try:
            print(Fore.GREEN+"****************** Establishing SSH connection to the remote instance ******************")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('3.111.66.135', username='ubuntu', password='', key_filename='cptblackbeardsEC2Instance.pem')
            print(Fore.GREEN+"****************** Connection Established  ******************")
            print(Fore.GREEN+"****************** Running Docker Compose Operation that starts containers nginx flask & mongo  ******************")
            print(Style.RESET_ALL)
            stdin,stdout, stderr = ssh.exec_command('pwd')
            self.showSSHOutput(stdout.readlines())

            stdin,stdout, stderr = ssh.exec_command('cd nginx-flask-mongo && docker compose up -d',get_pty=True)
            self.showSSHOutPutLongRunningCommand(stdout)

            print(Fore.GREEN+"****************** Docker Compose Operation Finished Successfully  ******************")
            print(Fore.GREEN+"****************** Running docker ps command to verify  ******************")
            print(Style.RESET_ALL)

            stdin,stdout, stderr = ssh.exec_command('docker ps')
            self.showSSHOutPutLongRunningCommand(stdout)

            print(Fore.GREEN+"****************** Performing curl on localhost:80  ******************")
            print(Style.RESET_ALL)
            stdin,stdout, stderr = ssh.exec_command('curl localhost:80')
            self.showSSHOutPutLongRunningCommand(stdout)

            print(Fore.GREEN+"****************** Stopping the containers now  ******************")
            print(Style.RESET_ALL)

            stdin,stdout, stderr = ssh.exec_command('docker compose down')
            self.showSSHOutput(stdout.readlines())

            ssh.close()
        except Exception as e:
            print(e)
            print(Fore.RED+"----------------- No such container is present on the remote instance     -------------------")
            print(Style.RESET_ALL)

    def showSSHOutput(self, input):
        if(input!=[]):
            print(input)
        else:
            pass

    def showSSHOutPutLongRunningCommand(self,input):
        for line in iter(input.readline, ""):
            print(line, end="")


    
            





            
    
    



       
        
