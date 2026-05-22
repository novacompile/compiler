import unittest

from ai_compiler import compile_code, list_languages


class AICompilerTests(unittest.TestCase):
    def test_lists_supported_languages(self):
        self.assertEqual(
            list_languages(),
            ["python", "javascript", "typescript", "go", "rust", "java", "cpp"],
        )

    def test_compiles_malformed_print_typo(self):
        compiled = compile_code("prnit hello world", "python")
        self.assertEqual(compiled.strip(), 'print("hello world")')

    def test_compiles_assignments_and_print_for_javascript(self):
        source = "value::10\nprint value"
        compiled = compile_code(source, "javascript")
        self.assertIn("let value = 10;", compiled)
        self.assertIn("console.log(value);", compiled)

    def test_rejects_unsupported_language(self):
        with self.assertRaises(ValueError):
            compile_code("print x", "kotlin")


if __name__ == "__main__":
    unittest.main()
