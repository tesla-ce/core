====
VLE
====

Read VLE information
-------------------------------
.. http:get:: /api/v2/vle/(int:vle_id)/

   :reqheader Authorization: JWT with Institution Administration privileges

   :param vle_id: VLE unique ID
   :type vle_id: int

   :statuscode 200: Ok
   :statuscode 404: VLE not found


List Courses in a VLE
----------------------
.. http:get:: /api/v2/vle/(int:vle_id)/course/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int

   :statuscode 200: Ok
   :statuscode 404: VLE not found


Create a new Course
-------------------------
.. http:post:: /api/v2/vle/(int:vle_id)/course/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int

   :<json string code: A code or short name for the course.
   :<json string vle_course_id: The unique ID for this course in the VLE.
   :<json string description: A description for this course.
   :<json datetime start: When the course starts.
   :<json datetime end: When the course ends.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: VLE not found


Read Course information
-------------------------------
.. http:get:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int

   :statuscode 200: Ok
   :statuscode 404: VLE not found
   :statuscode 404: Course not found


Update Course information
-------------------------------
.. http:put:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: VLE not found
   :statuscode 404: Course not found


Delete a Course
----------------------
.. http:delete:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int

   :statuscode 204: No Content
   :statuscode 404: VLE not found
   :statuscode 404: Course not found




List Activities in a VLE Course
--------------------------------
.. http:get:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/activity/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int

   :statuscode 200: Ok
   :statuscode 404: VLE not found
   :statuscode 404: Course not found


Create a new Activity
-------------------------
.. http:post:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/activity/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int

   :<json string vle_activity_type: The type of activity in the VLE.
   :<json string vle_activity_id: The id of the activity in the VLE.
   :<json string description: A description for this activity.
   :<json bool enabled: Whether TeSLA is enabled for this activity.
   :<json datetime start: When the activity starts.
   :<json datetime end: When the activity ends.
   :<json json conf: Generic activity configuration.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: VLE not found


Read Activity information
-------------------------------
.. http:get:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/activity/(int:activity_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int
   :param activity_id: Activity unique ID
   :type activity_id: int

   :statuscode 200: Ok
   :statuscode 404: VLE not found
   :statuscode 404: Course not found
   :statuscode 404: Activity not found


Update Activity information
-------------------------------
.. http:put:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/activity/(int:activity_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int
   :param activity_id: Activity unique ID
   :type activity_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: VLE not found
   :statuscode 404: Course not found
   :statuscode 404: Activity not found


Delete an Activity
-------------------
.. http:delete:: /api/v2/vle/(int:vle_id)/course/(int:course_id)/activity/(int:activity_id)/

   :reqheader Authorization: JWT with Institution Administration/VLE privileges

   :param vle_id: VLE unique ID
   :type vle_id: int
   :param course_id: Course unique ID
   :type course_id: int
   :param activity_id: Activity unique ID
   :type activity_id: int

   :statuscode 204: No Content
   :statuscode 404: VLE not found
   :statuscode 404: Course not found
   :statuscode 404: Activity not found


List Course learners
--------------------


Add a learner to a course
--------------------------


Remove a learner from a course
-------------------------------


List Course instructors
------------------------


Add an instructor to a course
------------------------------


Remove an instructor from a course
-----------------------------------




TODO: Add assessment documentation

