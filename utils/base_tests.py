from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time


class BaseModelTestCase(TestCase):

    model_class = None
    required_input = {}  # dict containing fields and values for successful validation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert issubclass(self.model_class, Model)
        assert isinstance(self.required_input, dict)

    def initiate_model(self, field, value):
        # Create model with one field altered from required_input.
        values = self.required_input.copy()
        values[field] = value
        return self.model_class(**values)  # pylint: disable=not-callable

    def default_model(self):
        # Create model from required_input.
        return self.model_class(**self.required_input.copy())  # pylint: disable=not-callable

    def _field_input_acceptance_test(self, field, value, is_valid, error_class, error_message):
        # Private method containing base code for running model validation tests
        model = self.initiate_model(field, value)
        if is_valid:
            model.full_clean()
            self.assertEqual(getattr(model, field), value)
        else:
            error = ValidationError
            if error_class:
                error = error_class
            if error_message:
                with self.assertRaisesRegex(error, error_message):
                    model.full_clean()
            else:
                with self.assertRaises(error):
                    model.full_clean()

    def field_should_accept_input(self, field, value):
        # Test that putting specified value in specified field should result in successful model validation
        self._field_input_acceptance_test(field=field, value=value, is_valid=True, error_class=None, error_message=None)

    def field_should_not_accept_input(self, field, value, error_class=None, error_message=None):
        """
        Test that putting specified value in specified field should not result in successful model validation.
        An error class and it's message can be additionally specified for TestCase assertion.
        Specifying error_message results in calling assertRaisesRegexp(), comparing it with received message.
        Leaving error_message empty will result in calling assertRaises().
        Leaving error_class empty will result in assertion for ValidationError by default.
        """
        self._field_input_acceptance_test(
            field=field, value=value, is_valid=False, error_class=error_class, error_message=error_message
        )

    def field_should_accept_null(self, field):
        # Test that leaving specified value empty should result in successful model validation.
        self.field_should_accept_input(field, None)

    def field_should_not_accept_null(self, field, error_class=None, error_message=None):
        """
        Test that putting specified value in specified field should not result in successful model validation.
        Support for specifying error class and error message is preserved in case a special behavior is expected.
        """
        self.field_should_not_accept_input(
            field=field, value=None, error_class=error_class, error_message=error_message
        )

    def field_auto_now_test(self, auto_field, update_field, value):
        """
        Test that timestamp field with auto_now flag set to true should change on model update.
            auto_field -> field with auto_now flag to be tested
            update_field -> field that should be updated for test's purpose
            value -> correct input for field that should be updated
        WARNING: It is assumed that the field is of DateTime type.
        Using any other time-related type can result in fail!
        """
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

    def field_should_have_non_null_default(self, field, value=None):
        """
        Test that specified field should be given default non-null value,
        when model is saved without having it's value assigned.
        Expected default value can be additionally specified for better accuracy.
        """
        model = self.default_model()
        model.full_clean()
        model.save()
        if value:
            self.assertEqual(getattr(model, field), value)
        self.assertIsNotNone(getattr(model, field))

    def key_should_not_accept_incorrect_input(self, field, value, error_message=None):
        """
        Test that creating model with specified incorrect value for specified foreign key field should fail.
        An expected error message can be additionally specified.
        """
        if error_message:
            with self.assertRaisesRegex(ValueError, error_message):
                self.initiate_model(field, value)
        else:
            with self.assertRaises(ValueError):
                self.initiate_model(field, value)


class BaseSerializerTestCase(TestCase):
    serializer_class = None

    def setUp(self):
        super().setUp()
        self.required_input = {}

    def initiate_serializer(self, field, value):
        # Create serializer with one field altered from required_input
        self.required_input[field] = value
        return self.serializer_class(data=self.required_input)  # pylint: disable=not-callable

    def default_serializer(self):
        # Create serializer from required_input
        return self.serializer_class(data=self.required_input)  # pylint: disable=not-callable

    def _field_input_acceptance_test(self, field, value, should_be_valid, error_message=None):
        # Private method containing base code for running serializer validation tests
        serializer = self.initiate_serializer(field, value)
        is_valid = serializer.is_valid()
        self.assertEqual(
            is_valid,
            should_be_valid,
            msg=f"Serializer is {is_valid}, but should be {should_be_valid} for {field} = {value}",
        )
        if error_message is not None:
            self.assertEqual(str(serializer.errors[field][0]), error_message)

    def field_should_accept_input(self, field, value):
        # Test that putting specified value in specified field should result in successful serializer validation
        self._field_input_acceptance_test(field=field, value=value, should_be_valid=True)

    def field_should_not_accept_input(self, field, value, error_message=None):
        # Test that putting value in specified field should not result in successful serializer validation
        self._field_input_acceptance_test(field=field, value=value, should_be_valid=False, error_message=error_message)

    def field_should_accept_null(self, field):
        # Test that leaving specified field empty should result in successful serializer validation
        self.field_should_accept_input(field, None)

    def field_should_not_accept_null(self, field):
        # Test that leaving specified field empty should not result in successful serializer validation
        self.field_should_not_accept_input(field, None)
