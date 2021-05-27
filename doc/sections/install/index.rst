Installation
=============

Services
--------
In order to work, TeSLA CE needs a set of services ready to use:

* Database (MySQL, PostgreSQL)
* HashiCorp Vault
* RabbitMQ
* Redis
* MinIO

The configuration and credentials to access those services is required in order to perform the initial setup of the system

Initial Setup
-------------

The initial setup process will prepare all the services in order to be used by TeSLA CE. In production scenarios
some of the services can be replaced by Amazon equivalents. In concrete:

* RDS database
* SQS instead of RabbitMQ
* S3 instead of MinIO
* Elastic Cache instead of Redis
* HashiCorp also provides a commercial version for Vault as a service

Is expected that all services are already available and ready to use for the installation.
If you want to deploy the services as part of the TeSLA CE system, see the Installing Services section.
To install TeSLA CE, follow those steps from any computer with access to the services:

1. Install database connector dependencies

.. code-block:: bash

   sudo apt-get install -y libpq-dev python3-dev python3-psycopg2 libmysqlclient-dev

2. Install the tesla-ce package (it is also possible to work with virtual environments)

.. code-block:: bash

   pip install tesla-ce

3. Generate a base configuration file. The installation script will try to store the file at
``/etc/tesla/tesla-ce.cfg`` and if it have no enough permissions, the file will be stored in the
local folder. Choose the base domain where TeSLA will be installed.

.. code-block:: bash

   tesla_ce generate_config [--with-services] <domain>

If you want to deploy the services as part of the deployment stage, add the --with-services flag, that
will generate all required credentials for the services.

4. Modify the generated configuration file ``nano /etc/tesla/tesla.cfg`` or ``nano tesla.cfg``:
   1. Provide database configuration options.
   2. Provide HashiCorp configuration. If Vault is already initialized, provide the root token and
   unsealing keys if it is sealed. If it is not initialized, just provide the URL to the service API.
   3. Provide RabbitMQ configuration.
   4. Provide Redis configuration.
   5. Provide MinIO configuration.

5. Check the configuration file. If you are deploying the services as part of the TeSLA deployment,
before continue you need to deploy the services. See the service deployment section.

.. code-block:: bash

   tesla_ce initial_setup --check

6. Run the configuration process. During the process, all created credentials will be stored
   in the configuration file. **Keep this file safe**, as it contains the administration
   keys, which are not stored anywhere else. If Vault is managed by TeSLA CE, this file will be required
   in order to unseal Vault. Those credentials will be also required to install providers and updates.

.. code-block:: bash

   tesla_ce initial_setup

Once the initial setup is done, TeSLA CE can be deployed.

Core Deployment
---------------

TeSLA CE system core consists of the following modules:

* **API:** Restful API to manage the system and to integrate with external systems and instrument providers.
* **LAPI:** The **Learners API** is a set of Restful services that are used by learners to interact with TeSLA CE.
* **Dashboards:** This module provides the web interfaces with TeSLA CE, including the LTI integration.
* **Worker** This module perform background coordination and periodic tasks.
* **Beat** This module activates periodic tasks.

TeSLA CE provides helper methods to perform the deployment in different Docker orchestrator systems.

Docker Swarm
************
The Swarm deployment will create a Docker Stack definition file and all credentials.

.. code-block:: bash

   tesla_ce deploy_core --mode=swarm --out=./deploy

Start the provided stack file on a master of your Docker Swarm cluster. First create the networks used by TeSLA:

.. code-block:: bash

   docker network create --driver overlay tesla_public
   docker network create --driver overlay tesla_private

Deploy the load balancer. In case services are deployed by TeSLA CE, the load balancer will be deployed after services:

.. code-block:: bash

   docker stack deploy -c ./deploy/tesla_lb.yml tesla

And finally deploy the TeSLA core elements:

.. code-block:: bash

   docker stack deploy -c ./deploy/tesla_core.yml tesla


Installing a VLE
---------------------
The communication between the VLE and TeSLA is performed by the VLE plugin. The list of supported VLEs are:

* Moodle

In order to connect your VLE to TeSLA, first install the plugin on your VLE following the instructions provided by
the plugin.

Register the VLE to TeSLA:

.. code-block:: bash

   tesla_ce register_vle --type=moodle my_vle

Once registered, the configuration values for the VLE plugin will be printed out. Use those values to setup the plugin.




Instrument providers
---------------------

Instrument providers are the modules that process the learners' data, by processing it directly or sending it to
an external system to be processed. Check the list of available providers.

1. Install a provider providing the tesla-ce configuration file used in the initial setup step and a configuration file
for the provider.

.. code-block:: bash

   tesla_ce install_provider --config-file=provider.cfg

2. Deploy the provider on a Docker orchestration system.

Docker Swarm
************
The Swarm deployment will create a Docker Stack definition file.

.. code-block:: bash

   tesla_ce deploy_provider --mode=swarm --out-file=tesla_provider.yml

Start the provided stack file on a master of your Docker Swarm cluster.

.. code-block:: bash

   docker stack deploy -c tesla_provider.yml tesla
