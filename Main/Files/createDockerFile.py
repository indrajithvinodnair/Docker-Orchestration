'''create a docker file using user specified file name, file path and image name'''
import os
import shutil
import docker
import configparser
class fileOps:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.dst_path = self.config['CREDENTIALS']['destination_path_for_built_docker_file']
        self.filename=""
        self.filepath=""
        self.imagename=""
        self.pythonversion=""
        self.dockerdirectory=self.config['CREDENTIALS']['docker_build_directory']
        self.dockerrepositoty=self.config['CREDENTIALS']['dockerhub_repository']

    def getSourceFile(self):
        print("create a docker file")
        self.filename=input("Enter the name of the image and its tag (imagename:tag) : ")
        self.filepath=input("Enter the full path to the file (including filename): ")
        self.imagename=input("Enter the name of the image: ")
        self.pythonversion = input("Enter the python version to use: ")

        try:
            if(os.path.isfile(self.filepath)):
                src_path = self.filepath
                shutil.copy(src_path, self.dst_path)
                print('Copied program files')
                    
        except Exception as e:
            print(e)
            print("File path not found")

    def createDockerFile(self):
        with open("Dockerfile", "w") as f:
            f.write("FROM python:"+self.pythonversion+"-slim\n")
            file_name = os.path.basename(self.filepath)
            f.write("COPY "+file_name+" /home/dockerimages/\n")
            f.write("WORKDIR /home/dockerimages\n")
            f.write("CMD [\"python\", \""+file_name+"\"]\n")

    def createDockerImage(self):
        print("creating the docker image: "+self.filename)
        try:
            client=docker.from_env()
            response = client.images.build(path=self.dst_path, tag=self.dockerrepositoty+self.filename)
            print(response)
            print("image created with tag: "+self.dockerrepositoty+self.filename)
        except Exception as e:
            print(e)

    def getimagename(self):
        return self.dockerrepositoty+self.filename





# file = fileOps()
# file.getSourceFile()
# file.createDockerFile()
# file.createDockerImage()
            

        

    
