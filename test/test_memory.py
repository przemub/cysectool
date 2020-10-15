import os
import unittest

from src.api import Memory


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = Memory.get_instance()

    def test_singleton(self):
        self.assertIs(self.memory, Memory.get_instance())
        self.assertIs(Memory.get_instance(), Memory.get_instance())

    def test_cant_init_twice(self):
        self.assertRaises(Exception, Memory)

    def test_import_templates(self):
        """Verify all templates get imported"""
        self.assertEqual(
            len(self.memory.templates),
            sum(
                1
                for file in os.listdir("doc/templates/")
                if file.endswith(".json")
            ),
        )


if __name__ == "__main__":
    unittest.main()
