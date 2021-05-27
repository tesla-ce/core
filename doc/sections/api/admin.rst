===============
Administration
===============

Instruments
============

List Instruments
-----------------
.. http:get:: /api/v2/admin/instrument/

   :reqheader Authorization: JWT with Global Administration privileges

   :statuscode 200: Ok


Create a new instrument
-------------------------
.. http:post:: /api/v2/admin/instrument/

   :reqheader Authorization: JWT with Global Administration privileges

   :<json string acronym: A unique acronym for the institution
   :<json string name: The full name of the institution
   :<json boolean external_ic: Whether the Informed Consent is managed externally for this institution. If enabled,
                               is assumed that all learners have signed an Informed Consent.
   :<json string mail_domain: Domain for users in this institution. If provided, all users in this institution must
                               provide an email in this domain.

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.


Read instrument information
-------------------------------
.. http:get:: /api/v2/admin/instrument/(int:instrument_id)/

   :reqheader Authorization: JWT with Global Administration privileges

   :param instrument_id: Instrument unique ID
   :type instrument_id: int

   :statuscode 200: Ok
   :statuscode 404: Instrument not found


Update instrument information
-------------------------------
.. http:put:: /api/v2/admin/instrument/(int:instrument_id)/

   :reqheader Authorization: JWT with Global Administration privileges

   :param instrument_id: Instrument unique ID
   :type instrument_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Instrument not found


Delete an instrument
----------------------
.. http:delete:: /api/v2/admin/instrument/(int:instrument_id)/

   :reqheader Authorization: JWT with Global Administration privileges

   :param instrument_id: Instrument unique ID
   :type instrument_id: int

   :statuscode 204: No Content
   :statuscode 404: Instrument not found


Institutions
============

Create a new institution
-------------------------
.. http:post:: /api/v2/admin/institution/

   :reqheader Authorization: JWT with Global Administration privileges

   :<json string acronym: A unique acronym for the institution
   :<json string name: The full name of the institution
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

   :statuscode 201: Created
   :statuscode 400: Invalid information provided. The response contains the description of the errors.


Update institution information
-------------------------------
.. http:put:: /api/v2/admin/institution/(int:institution_id)/

   :reqheader Authorization: JWT with Global Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 200: Ok
   :statuscode 400: Invalid information provided. The response contains the description of the errors.
   :statuscode 404: Institution not found


Delete an institution
----------------------
.. http:delete:: /api/v2/admin/institution/(int:institution_id)/

   :reqheader Authorization: JWT with Global Administration privileges

   :param institution_id: Institution unique ID
   :type institution_id: int

   :statuscode 204: No Content
   :statuscode 404: Institution not found

