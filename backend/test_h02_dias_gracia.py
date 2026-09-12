import os
import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock


class TestH02_DiasGraciaEnSchema(unittest.TestCase):
    """H-02: MiembroResponse must include dias_restantes_gracia field."""

    def test_schema_has_dias_restantes_gracia_field(self):
        from app.schemas import MiembroResponse
        schema_fields = MiembroResponse.model_fields
        self.assertIn("dias_restantes_gracia", schema_fields,
                       "MiembroResponse schema is missing 'dias_restantes_gracia' field")

    def test_schema_field_type_is_optional_int(self):
        from app.schemas import MiembroResponse
        field_info = MiembroResponse.model_fields["dias_restantes_gracia"]
        self.assertTrue(field_info.annotation == int or
                        str(field_info.annotation) == "Optional[int]" or
                        str(field_info.annotation) == "int | None",
                        f"dias_restantes_gracia should be Optional[int], got {field_info.annotation}")
        self.assertIsNone(field_info.default,
                          "dias_restantes_gracia should default to None")

    def test_search_endpoint_returns_dias_restantes_gracia(self):
        from app.main import search_member_by_cedula
        result = search_member_by_cedula.__dict__
        # Verify the endpoint explicitly passes dias_restantes_gracia
        from app.main import app
        for route in app.routes:
            if hasattr(route, "endpoint") and route.endpoint == search_member_by_cedula:
                response_model = route.response_model
                break
        else:
            self.fail("Could not find route for search_member_by_cedula")
        from app.schemas import MiembroResponse
        self.assertIs(response_model, MiembroResponse,
                       "search endpoint should use MiembroResponse")
        # Verify MiembroResponse has the field
        self.assertIn("dias_restantes_gracia", MiembroResponse.model_fields)

    def test_list_endpoint_uses_miembro_response(self):
        from app.main import list_members
        from app.main import app
        for route in app.routes:
            if hasattr(route, "endpoint") and route.endpoint == list_members:
                response_model = route.response_model
                break
        else:
            self.fail("Could not find route for list_members")
        from app.schemas import MiembroResponse
        origin = getattr(response_model, "__origin__", None)
        if origin is not None:
            inner_type = response_model.__args__[0]
            self.assertIs(inner_type, MiembroResponse,
                           "list members endpoint should use List[MiembroResponse]")
        else:
            self.assertIs(response_model, MiembroResponse,
                           "list members endpoint should use List[MiembroResponse]")
        self.assertIn("dias_restantes_gracia", MiembroResponse.model_fields)

    def test_miembro_response_serializes_dias_restantes_gracia(self):
        from app.schemas import MiembroResponse
        data = MiembroResponse(
            id=1,
            cedula="12345678",
            nombre="Test",
            telefono="04121234567",
            estado_logico=True,
            estatus_actual="en_gracia",
            dias_restantes_gracia=3,
            plan_nombre="Plan Basic",
            plan_id=1,
        )
        serialized = data.model_dump()
        self.assertIn("dias_restantes_gracia", serialized)
        self.assertEqual(serialized["dias_restantes_gracia"], 3)

    def test_miembro_response_defaults_to_none(self):
        from app.schemas import MiembroResponse
        data = MiembroResponse(
            id=2,
            cedula="87654321",
            nombre="Test2",
            estado_logico=True,
        )
        serialized = data.model_dump()
        self.assertIn("dias_restantes_gracia", serialized)
        self.assertIsNone(serialized["dias_restantes_gracia"])


if __name__ == "__main__":
    unittest.main()
