==============
Institution
==============
TeSLA CE allows to define multiple institutions. Each institution will be treated
in a independent way, having their learners, instructors and users. The computation
resources will be shared. New institutions can be created, updated and deleted using
the administration API. Once created, institutions can be managed by their administrators.

List Institutions
------------------
.. http:get:: /api/v2/institution/

   :reqheader Authorization: JWT with Global Administration privileges

   :statuscode 200: Ok


Read institution information
-------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found


Change institution properties
------------------------------
.. http:put:: /api/v2/institution/(int:institution_id)/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :<json boolean external_ic: Whether the Informed Consent is managed externally for this institution. If enabled,
                               is assumed that all learners have signed an Informed Consent.
   :<json string mail_domain: Domain for users in this institution. If provided, all users in this institution must
                               provide an email in this domain.
   :<json boolean disable_vle_learner_creation: If enabled, VLE cannot create new learners. Learners can only be created
                                                with the institution API.
   :<json boolean disable_vle_instructor_creation: If enabled, VLE cannot create new instructors. Instructors can
                                                   only be created with the institution API.
   :<json boolean disable_vle_user_creation: If enabled, VLE cannot create new institution users. Users can only be
                                             created with the institution API.


   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found


Informed Consent
================
The "Informed Consent" is the legal document a learner must accept before any data from learner is captured.
Informed Consents belong to institutions, and are ordered by a version value as "X.Y.Z". When the institution informed
consent changes in the first two positions (X, Y), it is considered a major change, and invalidate previous
informed consent, what means all learners need to accept the new one before submitting any new data.
Small changes, like typos can be generated as minor changes. In this case, where only the Z
value changes, the system will suggest learners to update the informed consent, but will allow them to continue.
For each informed consent, the legal document in different languages can be stored.

List informed consents
-----------------------
.. http:get:: /api/v2/institution/(int:institution_id)/ic/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found


Create a new informed consent
-----------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/ic/

   :reqheader Authorization: JWT with Institution Legal privileges

   :<json string version: Version value. Must be unique for the institution.
   :<json datetime valid_from: When this informed consent takes effect.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found

Read informed consent information
---------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Informed consent unique ID
   :type consent_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found


Update informed consent
-----------------------
.. http:put:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/

   :reqheader Authorization: JWT with Institution Legal privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Institution unique ID
   :type consent_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found


Delete informed consent
-----------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/

   :reqheader Authorization: JWT with Institution Legal privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Institution unique ID
   :type consent_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found


List informed consent documents
-------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Informed consent unique ID
   :type consent_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found
   :statuscode 404: Informed consent document not found


Create a new informed consent document
--------------------------------------
The document for each language is provided by HTML and with an attached file.
.. http:post:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/

   :reqheader Authorization: JWT with Institution Legal privileges

   :<json string language: The language of the document
   :<json string html: The content in HTML format of the document

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found


Read informed consent document information
-------------------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/(str:language)/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Informed consent unique ID
   :type consent_id: int
   :param language: Language of the document
   :type language: str

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found
   :statuscode 404: Informed consent document not found


Update informed consent document
---------------------------------
.. http:put:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/(str:language)/

   :reqheader Authorization: JWT with Institution Legal privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Institution unique ID
   :type consent_id: int
   :param language: Language of the document
   :type language: str


   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found
   :statuscode 404: Informed consent document not found


Delete informed consent document
---------------------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/(str:language)/

   :reqheader Authorization: JWT with Institution Legal privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param consent_id: Institution unique ID
   :type consent_id: int
   :param language: Language of the document
   :type language: str

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Informed consent not found
   :statuscode 404: Informed consent document not found


Course Groups
=============
Course groups allow institutions to organize their courses in bigger groups. Each course group can have many courses
from the different VLEs of the institution and other groups. In this way, courses can be organized in semesters, degrees,
department or any other structure useful for the institution.

The only requirement for the course groups is to maintain a hierarchical structure without cycles.

List Groups
--------------
.. http:get:: /api/v2/institution/(int:institution_id)/group/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found

Create a new Group
---------------------
.. http:post:: /api/v2/institution/(int:institution_id)/group/

   :reqheader Authorization: JWT with Institution Admin privileges

   :<json int parent: Id of the parent group. Null if this group is not in another group.
   :<json string name: Name of the group.
   :<json string description: Description of the group.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found

Read group information
---------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Group not found

Update group
---------------
.. http:put:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Group not found


Delete group
---------------
.. http:delete:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Group not found


List courses in a group
------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/course/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Group not found

Add a course to a group
------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/course/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int

   :<json int id: Course ID.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Group not found
   :statuscode 404: Course not found


Delete a course from a group
-----------------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/group/(int:group_id)/course/(int:course_id)/

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param group_id: Group ID.
   :type group_id: int
   :param course_id: Course ID.
   :type course_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Group not found
   :statuscode 404: Course not found

SEND
====
Institutions can define categories for Special Education Needs and Disabilities. Each category defines a set
of options and a list of instruments that will be disabled. This allow the system to automatically adapts to
the SEND requirements of each learner.

List SEND Categories
---------------------
.. http:get:: /api/v2/institution/(int:institution_id)/send/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found

Create a new SEND Category
---------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/send/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :<json int parent: Id of the parent group. Null if this group is not in another group.
   :<json string description: Description for this category
   :<json json data: Options for this SEND category. A field 'enabled_options' with a list of enabled accessibility
       options in the set ('high_contrast', 'big_fonts', 'text_to_speech') and a field 'disabled_instruments' with the list
       of instrument Ids to disable.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found

Read SEND Category information
-------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/send/(int:send_id)/

   :reqheader Authorization: JWT with Institution privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param send_id: SEND category ID.
   :type send_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: SEND Category not found

Update SEND Category
---------------------
.. http:put:: /api/v2/institution/(int:institution_id)/send/(int:send_id)/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param send_id: SEND category ID.
   :type send_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: SEND Category not found


Delete SEND Category
---------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/send/(int:send_id)

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param send_id: SEND category ID.
   :type send_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: SEND Category not found


Institution Users
=================
TODO

Learners
========
Learners are a type of Institution Users. In addition to the information of the institution user,
each learner is provided with a learner_id value of type UUIDv4 that identifies this learner in a
unique manner in the TeSLA instance. This learner_id is provided to external services, like
data validators and instrument providers, which allows to prevent sharing the personal information
from learners.

List learners
--------------
.. http:get:: /api/v2/institution/(int:institution_id)/learner

   :reqheader Authorization: JWT with Institution Admin/Instructor privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found


Create a new Learner
---------------------
.. http:post:: /api/v2/institution/(int:institution_id)/learner

   :reqheader Authorization: JWT with Institution Admin privileges

   :<json string uid: Unique ID of this learner in the institution.
   :<json string email: Email of the learner. If institution mail_domain is provided, this email must be in this domain.
   :<json string first_name: First name of the learner.
   :<json string last_name: Last name of the learner.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found

Read learner information
---------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)

   :reqheader Authorization: JWT with Institution Admin/Instructor privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Update learner
---------------
.. http:put:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int


   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Delete learner
---------------
.. http:delete:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)

   :reqheader Authorization: JWT with Institution Admin/Legal privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int


   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Accept an Informed Consent for a learner
------------------------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)/ic

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int

   :<json string version: Informed consent version to assign

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Reject current Informed Consent of a learner
---------------------------------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)/ic

   :reqheader Authorization: JWT with Institution Admin privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Add SEND category to a learner
-------------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)/send/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int

   :<json int category: SEND Category ID
   :<json datetime expires_at: When the special need is temporal, provide the date when it disappears.
       For permanent needs, let it null.

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found
   :statuscode 404: SEND Category not found


Read SEND categories assigned to a learner
-------------------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)/send/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found


Remove a SEND Category from a learner
---------------------------------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/learner/(int:learner_id)/send/(int:send_assig_id)/

   :reqheader Authorization: JWT with Institution Admin/SEND privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param learner_id: Learner ID in the database.
   :type learner_id: int
   :param send_assig_id: Learner category assignation ID.
   :type send_assig_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: Learner not found
   :statuscode 404: SEND Category assignation not found


Instructors
===========
TODO


VLE
====

List VLEs
------------------
.. http:get:: /api/v2/institution/(int:institution_id)/vle/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found


Create a new VLE
-------------------------
.. http:post:: /api/v2/institution/(int:institution_id)/vle/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :<json string name: A unique name for this VLE
   :<json int type: The type of VLE
   :<json string url: The url to access this VLE
   :<json string client_id: The LTI 1.3 Client ID

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found


Read VLE information
-------------------------------
.. http:get:: /api/v2/institution/(int:institution_id)/vle/(int:vle_id)/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param vle_id: VLE unique ID
   :type vle_id: int

   :statuscode 200: Ok
   :statuscode 404: Institution not found
   :statuscode 404: VLE not found


Update VLE information
-------------------------------
.. http:put:: /api/v2/institution/(int:institution_id)/vle/(int:vle_id)/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param vle_id: VLE unique ID
   :type vle_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found
   :statuscode 404: VLE not found


Delete a VLE
----------------------
.. http:delete:: /api/v2/institution/(int:institution_id)/vle/(int:vle_id)/

   :reqheader Authorization: JWT with Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int
   :param vle_id: VLE unique ID
   :type vle_id: int

   :statuscode 204: No Content
   :statuscode 404: Institution not found
   :statuscode 404: VLE not found
