#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""User api serialize module."""
from django.contrib.auth.models import make_password
from rest_framework import serializers
from rest_framework import validators

from tesla_ce.models import User
from tesla_ce.models import InstitutionUser
from tesla_ce import get_default_client


class UserSerializer(serializers.ModelSerializer):
    """User serialize model module."""

    username = serializers.CharField(allow_blank=False,
                                     allow_null=False,
                                     validators=[
                                         validators.UniqueValidator(queryset=User.objects.all())
                                     ]
                                     )
    last_login = serializers.DateTimeField(read_only=True)
    first_name = serializers.CharField(required=False, default=None)
    last_name = serializers.CharField(required=False, default=None)
    email = serializers.EmailField(required=False, default=None,
                                   validators=[
                                       validators.UniqueValidator(queryset=User.objects.all())
                                   ]
                                   )
    password = serializers.CharField(write_only=True, default=None, allow_null=True)
    password2 = serializers.CharField(write_only=True, default=None, allow_null=True)
    institution = serializers.SerializerMethodField(read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)
    institution_id = serializers.IntegerField(write_only=True, allow_null=True, default=None)
    login_allowed = serializers.BooleanField(required=False, default=True, allow_null=False)
    uid = serializers.CharField(write_only=True, default=None, allow_null=True)

    is_staff = serializers.BooleanField(required=False, allow_null=False, default=False)
    inst_admin = serializers.BooleanField(required=False, allow_null=False, default=False)
    legal_admin = serializers.BooleanField(required=False, allow_null=False, default=False)
    send_admin = serializers.BooleanField(required=False, allow_null=False, default=False)
    data_admin = serializers.BooleanField(required=False, allow_null=False, default=False)

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Check passwords
        if attrs.get('login_allowed', True):
            if 'password' in attrs and attrs.get('password') != attrs.get('password2'):
                raise serializers.ValidationError('Passwords does not match')
            if 'password2' in attrs:
                del attrs['password2']
        else:
            attrs['login_allowed'] = False

        if 'institution_id' in attrs and attrs['institution_id'] == -1:
            attrs['institution_id'] = None

        if (self.instance is None or self.get_institution(self.instance) is None) and \
                attrs.get('institution_id') is not None and attrs.get('uid') is None:
            raise ValueError('uid value is required when assigning an institution')

        return super().validate(attrs)

    def get_institution(self, object):
        if hasattr(object, "institutionuser"):
            roles = []
            if hasattr(object.institutionuser, "instructor"):
                roles.append("INSTRUCTOR")
            if hasattr(object.institutionuser, "learner"):
                roles.append("LEARNER")
            if object.institutionuser.inst_admin:
                roles.append("ADMIN")
            if object.institutionuser.send_admin:
                roles.append("SEND")
            if object.institutionuser.legal_admin:
                roles.append("LEGAL")
            if object.institutionuser.data_admin:
                roles.append("DATA")

            return {
                "id": object.institutionuser.institution.id,
                "acronym": object.institutionuser.institution.acronym,
                "uid": object.institutionuser.uid,
                "roles": roles,
                "locale": object.institutionuser.locale,
            }

        return None

    def get_roles(self, object):
        roles = []
        inst = self.get_institution(object)
        if inst is not None:
            roles = inst['roles']
        if object.is_staff:
            roles.append('GLOBAL_ADMIN')

        return roles

    def create(self, validated_data):
        inst_data = None
        if 'institution_id' in validated_data and validated_data['institution_id'] is not None:
            inst_data = {
                'institution': validated_data['institution_id'],
                'uid': None,
                'inst_admin': False,
                'data_admin': False,
                'send_admin': False,
                'legal_admin': False,
                'login_allowed': False
            }
            if 'inst_admin' in validated_data and validated_data['inst_admin'] is not None:
                inst_data['inst_admin'] = validated_data['inst_admin']
            if 'data_admin' in validated_data and validated_data['data_admin'] is not None:
                inst_data['data_admin'] = validated_data['data_admin']
            if 'send_admin' in validated_data and validated_data['send_admin'] is not None:
                inst_data['send_admin'] = validated_data['send_admin']
            if 'legal_admin' in validated_data and validated_data['legal_admin'] is not None:
                inst_data['legal_admin'] = validated_data['legal_admin']
            if 'uid' in validated_data and validated_data['uid'] is not None:
                inst_data['uid'] = validated_data['uid']
            if 'login_allowed' in validated_data and validated_data['login_allowed'] is not None:
                inst_data['login_allowed'] = validated_data['login_allowed']
        if 'institution_id' in validated_data:
            del validated_data['institution_id']
        if 'inst_admin' in validated_data:
            del validated_data['inst_admin']
        if 'legal_admin' in validated_data:
            del validated_data['legal_admin']
        if 'data_admin' in validated_data:
            del validated_data['data_admin']
        if 'send_admin' in validated_data:
            del validated_data['send_admin']
        if 'uid' in validated_data:
            del validated_data['uid']
        if 'login_allowed' in validated_data:
            del validated_data['login_allowed']

        new_password = None
        if 'password' in validated_data:
            new_password = validated_data['password']
            del validated_data['password']

        user = super().create(validated_data)

        if inst_data is not None:
            # Disable password if necessary
            if not inst_data['login_allowed']:
                user.set_unusable_password()
                user.save()
                new_password = None

            # Create the related institution user
            user.institutionuser = InstitutionUser(institution_id=inst_data['institution'],
                                                   uid=inst_data['uid'],
                                                   login_allowed=inst_data['login_allowed'],
                                                   inst_admin=inst_data['inst_admin'],
                                                   legal_admin=inst_data['legal_admin'],
                                                   data_admin=inst_data['data_admin'],
                                                   send_admin=inst_data['send_admin'])
            user.institutionuser.save()
            user.save()
            user.institutionuser.refresh_from_db()

        if new_password:
            get_default_client().change_user_password(user.email, new_password)
            user.refresh_from_db()

        return user

    def update(self, instance, validated_data):
        has_inst = self.get_institution(instance) is not None
        new_inst = False

        # Check if we are adding a new institution
        if 'institution_id' in validated_data:
            if not has_inst and validated_data['institution_id'] is not None:
                # Create the related institution user
                instance.institutionuser = InstitutionUser(institution_id=validated_data['institution_id'],
                                                           uid=None,
                                                           login_allowed=False,
                                                           inst_admin=False,
                                                           legal_admin=False,
                                                           data_admin=False,
                                                           send_admin=False)
                new_inst = True
            elif has_inst and validated_data['institution_id'] is None:
                # Removing the institution
                has_inst = False
                instance.institutionuser.delete(keep_parents=True)
                instance.refresh_from_db()

        # Apply institution allowed fields modifications
        if has_inst or new_inst:
            modified = False
            if 'inst_admin' in validated_data:
                instance.institutionuser.inst_admin = validated_data['inst_admin']
                modified = True
            if 'send_admin' in validated_data:
                instance.institutionuser.send_admin = validated_data['send_admin']
                modified = True
            if 'legal_admin' in validated_data:
                instance.institutionuser.legal_admin = validated_data['legal_admin']
                modified = True
            if 'data_admin' in validated_data:
                instance.institutionuser.data_admin = validated_data['data_admin']
                modified = True
            if 'uid' in validated_data:
                instance.institutionuser.uid = validated_data['uid']
                modified = True
            if 'login_allowed' in validated_data:
                instance.institutionuser.login_allowed = validated_data['login_allowed']
                modified = True
            if 'institution_id' in validated_data:
                instance.institutionuser.institution_id = validated_data['institution_id']
                modified = True

            if modified or new_inst:
                instance.institutionuser.save()

        # If a new institution has been added, refresh objects to avoid data loose
        if new_inst:
            instance.save()
            instance.institutionuser.refresh_from_db()

        new_password = None
        if 'password' in validated_data:
            new_password = validated_data['password']
            del validated_data['password']

        updated_user = super().update(instance, validated_data)

        if new_password is not None:
            get_default_client().change_user_password(updated_user.email, new_password)

        return updated_user
