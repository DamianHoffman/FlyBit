import glob
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def skills():
    return sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class SkillDocs(unittest.TestCase):
    def test_there_are_four_skills(self):
        self.assertEqual([os.path.basename(os.path.dirname(p)) for p in skills()],
                         ["ab-test", "compliance-review", "new-automation", "sms-check"])

    def test_name_matches_directory(self):
        for p in skills():
            m = re.search(r"^name: (\S+)$", read(p), re.M)
            self.assertEqual(m.group(1), os.path.basename(os.path.dirname(p)))

    def test_scripts_are_documented_for_claude_code_and_chat(self):
        # Claude Code replaces ${CLAUDE_SKILL_DIR}; chat does not, so the relative path must also be in the text.
        for p in skills():
            txt = read(p)
            for script in glob.glob(os.path.join(os.path.dirname(p), "scripts", "*.py")):
                rel = "scripts/" + os.path.basename(script)
                self.assertIn("${CLAUDE_SKILL_DIR}/" + rel, txt, p)
                self.assertIn("python3 " + rel, txt, p)

    def test_referenced_files_exist(self):
        for p in skills():
            for ref in set(re.findall(r"references/[\w.-]+\.md", read(p))):
                self.assertTrue(os.path.exists(os.path.join(os.path.dirname(p), ref)), (p, ref))

    def test_every_reference_file_is_mentioned(self):
        for p in skills():
            txt = read(p)
            for ref in glob.glob(os.path.join(os.path.dirname(p), "references", "*.md")):
                self.assertIn("references/" + os.path.basename(ref), txt, ref)

    def test_frontmatter_has_no_colon_space_in_plain_scalars(self):
        # ': ' inside a plain YAML scalar breaks the frontmatter and blocks loading
        for p in skills():
            fm = re.match(r"^---\n(.*?)\n---\n", read(p), re.S).group(1)
            for line in fm.splitlines():
                self.assertNotIn(": ", line.partition(": ")[2], p)

    def test_cross_skill_references_point_to_existing_skills(self):
        names = {os.path.basename(os.path.dirname(p)) for p in skills()}
        for p in skills():
            for ref in re.findall(r"`(sms-check|compliance-review|ab-test|new-automation|new-campaign)`", read(p)):
                self.assertIn(ref, names, p)


if __name__ == "__main__":
    unittest.main()
