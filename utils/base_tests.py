from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import BaseSerializer


class BaseModelTestCase(TestCase):

    model_class = None
    required_input = {}             # dict containing fields and values for successful validation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert issubclass(self.model_class, Model)
        assert isinstance(self.required_input, dict)

    """
    Create model with one field altered from required_input.
    """
    def initiate_model(self, field, value):
        values = self.required_input.copy()
        values[field] = value
        return self.model_class(**values)

    """
    Create model from required_input.
    """
    def default_model(self):
        return self.model_class(**self.required_input.copy())

    """
    Private method containing base code for running model validation tests.
    """
    def _field_input_acceptance_test(self, field, value, is_valid, error_class, error_message):
        model = self.initiate_model(field, value)
        if is_valid:
            model.full_clean()
            self.assertEqual(getattr(model, field), value)
        else:
            error = ValidationError
            if error_class:
                error = error_class
            if error_message:
                with self.assertRaisesRegex(
                        error,
                        error_message,
                ):
                    model.full_clean()
            else:
                with self.assertRaises(
                        error
                ):
                    model.full_clean()

    """
    Test that putting specified value in specified field should result in successful model validation.
    """
    def field_should_accept_input(self, field, value):
        self._field_input_acceptance_test(
            field=field,
            value=value,
            is_valid=True,
            error_class=None,
            error_message=None,
        )

    """
    Test that putting specified value in specified field should not result in successful model validation.
    An error class and it's message can be additionally specified for TestCase assertion.
    Specifying error_message results in calling assertRaisesRegexp(), comparing it with received message.
    Leaving error_message empty will result in calling assertRaises().
    Leaving error_class empty will result in assertion for ValidationError by default.
    """
    def field_should_not_accept_input(self, field, value, error_class=None, error_message=None):
        self._field_input_acceptance_test(
            field=field,
            value=value,
            is_valid=False,
            error_class=error_class,
            error_message=error_message,
        )

    """
    Test that leaving specified value empty should result in successful model validation.
    """
    def field_should_accept_null(self, field):
        self.field_should_accept_input(field, None)

    """
    Test that putting specified value in specified field should not result in successful model validation.
    Support for specifying error class and error message is preserved in case a special behavior is expected.
    """
    def field_should_not_accept_null(self, field, error_class=None, error_message=None):
        self.field_should_not_accept_input(
            field=field,
            value=None,
            error_class=error_class,
            error_message=error_message,
        )

    """
    Test that timestamp field with auto_now flag set to true should change on model update.
        auto_field -> field with auto_now flag to be tested
        update_field -> field that should be updated for test's purpose
        value -> correct input for field that should be updated
    WARNING: It is assumed that the field is of DateTime type.
    Using any other time-related type can result in fail!
    """
    def field_auto_now_test(self, auto_field, update_field, value):
        with freeze_time(timezone.now()) as frozen_datetime:
            model = self.default_model()
            model.full_clean()
            model.save()
            frozen_datetime.tick()
            setattr(model, update_field, value)
            model.full_clean()
            model.save()
            current_value = getattr(model, auto_field)
            self.assertEqual(current_value, timezone.now())

    """
    Test that specified field should be given default non-null value,
    when model is saved without having it's value assigned.
    Expected default value can be additionally specified for better accuracy.
    """
    def field_should_have_non_null_default(self, field, value=None):
        model = self.default_model()
        model.full_clean()
        model.save()
        if value:
            self.assertEqual(getattr(model, field), value)
        self.assertIsNotNone(getattr(model, field))

    """
    Test that creating model with specified incorrect value for specified foreign key field should fail.
    An expected error message can be additionally specified.
    """
    def key_should_not_accept_incorrect_input(self, field, value, error_message=None):
        if error_message:
            with self.assertRaisesRegex(
                    ValueError,
                    error_message,
            ):
                self.initiate_model(field, value)
        else:
            with self.assertRaises(
                    ValueError,
            ):
                self.initiate_model(field, value)


class BaseSerializerTestCase(TestCase):

    serializer_class = None
    required_input = {}             # dict containing fields and values for successful validation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert issubclass(self.serializer_class, BaseSerializer)
        assert isinstance(self.required_input, dict)

    """
    Create serializer with one field altered from required_input.
    """
    def initiate_serializer(self, field, value):
        values = self.required_input.copy()
        values[field] = value
        return self.serializer_class(data=values)

    """
    Create serializer from required_input.
    """
    def default_serializer(self):
        return self.serializer_class(data=self.required_input)

    """
    Private method containing base code for running serializer validation tests.
    """
    def _field_input_acceptance_test(self, field, value, is_valid):
        serializer = self.initiate_serializer(field, value)
        self.assertEqual(serializer.is_valid(), is_valid)

    """
    Test that putting specified value in specified field should result in successful serializer validation.
    """
    def field_should_accept_input(self, field, value):
        self._field_input_acceptance_test(
            field=field,
            value=value,
            is_valid=True
        )

    """
    Test that putting value in specified field should not result in successful serializer validation.
    """
    def field_should_not_accept_input(self, field, value):
        self._field_input_acceptance_test(
            field=field,
            value=value,
            is_valid=False
        )

    """
    Test that leaving specified field empty should result in successful serializer validation.
    """
    def field_should_accept_null(self, field):
        self.field_should_accept_input(field, None)

    """
    Test that leaving specified field empty should not result in successful serializer validation.
    """
    def field_should_not_accept_null(self, field):
        self.field_should_not_accept_input(field, None)
