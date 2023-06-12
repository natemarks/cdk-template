# Flat Store
!!! DO NOT PUT SECURE DATA IN FLAT STORE !!!
Use something like AWS Secrets Manager. CDK works nicely with that.
!!! DO NOT PUT SECURE DATA IN FLAT STORE !!!

The  flat store is a simple structure intended to contain may thousands of configuration settings for an application environment, while still making it easy to manage, validate and compare the data across releases and environments. Every stack in the CDK project uses a data from the flatstore as input.

benefit 1: The simple structure makes it easy to create a flatstore for a new environment from another environment, then automatically change and compare them.

benefit 2: it's a great place to gather and store configuration data external to the project: ex. discover details about remote connections  in a StackConfig class and store then in the stack dataclass.

benefit 3: validate, troubleshoot and maintain the project. It's convenient to be able to parse and validate the configuration separate from the CDK logic.


## Schema
The flat store is a simple way to store all the configuration input to deploy an application to an environment. It's a simple, minimally nested key-value object. When it's deserialized, the values can be simple strings, integers or booleans. They can also be a list of those. But there's no further Dict (map nesting permitted).

 - string
 - int
 - bool
 - List[string | int | bool]
 - Dict[string, string | int | bool]

The key is a string that's delimited by a separator. The separator makes the keys look like paths. The purpose is to make it easy to group related key/values together. This is an example of a flat store serialized to JSON:

```json
{
  "/app/env/admin_team": "Operations",
  "/app/env/aws_account_name": "MyApp Dev",
  "/app/env/config_id": "dev",
  "/app/env/stack_prefix": "Dev",
  "/app/env/aws_account_number": "0123456789",
  "/app/env/default_domain": "dev.myapp.com",
  "/app/env/default_region": "us-east-1",
  "/app/env/app_vpc/cidr": "10.101.0.0/16",
  "/app/env/app_vpc/max_azs": 2,
  "/app/env/app_vpc/termination_protection": false,
  "/app/env/eks_cluster/hello/api_version": "v1",
  "/app/env/eks_cluster/hello/kind": "Pod",
  "/app/env/eks_cluster/hello/app_name": "hello",
  "/app/env/eks_cluster/hello/app_image": "paulbouwer/hello-kubernetes:1.5",
  "/app/env/eks_cluster/hello/app_port": 8080
}
```

In this example, the keys that begin with "/app/env/" are all related. They are the configuration  values that are common to every stack in the application.

The keys that begin with "/app/env/app_vpc/" represent the settings for a stack of type app_vpc.  It is a unique stack meaning that there's only one such stack in the application AND that it's required in order for the environment to be valid.

The keys that begin with "/app/env/eks_cluster/hello/" represent settings for a stack of type "eks_cluster" and with a config_id of "hello". This is a named stack. That means that there may be more than one eks cluster in the application and they're  each identified by a unique config_id.


