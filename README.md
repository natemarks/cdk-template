# cdk-template
This project is my starting point for AWS Infrastructure-as-Code projects in AWS. It has a small collection of tools and patterns I use regularly. The general idea is to loosely couple the configuration data from the CDK code. 

The [flat store](doc%2FFLATSTORE.md) is a simple dict that can contain the  many thousands of configuration settings required to deploy the application to an environment. The format makes it easy to generate, save,compare and version the ENTIRE configuration. 

This is important when:
 - promoting new configurations between environments
 - automatically gathering external configuration data
 - troubleshooting and maintaining the project

 As with all CDK projects, there is a single App object that contains many Stack objects. This project further subclasses the Stacks into Unique and Named stacks. Unique stacks exist exactly once in an App. There can be zero or many instances of Named stacks in an app, each with its own unique config_id.
![template stacks](doc%2Fimages%2Fenvironments-stacks.jpg)

The Environment class is created from the flat store data and drives stack creation. Deployments are driven from subclasses of the Environment class because some changes are too big or complex to be executed cleanly without substantially changing an environment. in these cases we carefully migrate from one environment subclass to another.
![environments-timeline.jpg](doc%2Fimages%2Fenvironments-timeline.jpg)

## Getting Started

To get started, just clone the project, delete the .git directory and rename the project directory.  'make static' should work out of the box, which run the base tests

Change the iac tag in app.py. I use this to keep track of what IAC project manages a particular resource.
```
cdk.Tags.of(app).add("iac", "cdk-template")
```

## TODO: Document Template Features
flat store: there are some simple examples for using the flat store. 
Environment class: is the object used to organize the flat store data for use in the classes
stack Config class ->  stack dataclass -> stack class: 
Every Stack class has  a matching Config class that is used to generate the stack dataclass. the config class is a good way to gather external data and pack it into the flatstore.
pytests
golden files: the tests compare the result to expected golden files.  If you change the logic  or input, the golden file changes. make update_golden runs does this update automatically.
makefile
