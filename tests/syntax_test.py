import sublime
import unittest

class SyntaxTestCase(unittest.TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.settings().set('auto_indent', False)
        self.reset_scopes()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def set_syntax_file(self, syntax_file):
        assert(self.view)
        self.view.set_syntax_file(syntax_file)
        self.reset_scopes()

    def set_text(self, string):
        self.view.run_command("select_all")
        self.view.run_command("left_delete")
        self.view.run_command("insert", {"characters": string})
        self.reset_scopes()

    def check_in_scope(self, patterns, scope):
        """
        Checks that region(s) found by pattern(s) lie(s) within
        the specified scope.
        """
        self.check_patterns(patterns, scope, self.in_scope)

    def check_in_single_scope(self, patterns, scope):
        """
        Checks that region(s) found by pattern(s) lie(s) within
        the specified scope and no other scopes
        are present in that region(s).
        """
        self.check_patterns(patterns, scope, self.in_single_scope)

    def check_eq_scope(self, patterns, scope):
        """
        Checks that begin and end positions of region(s)
        found by pattern(s) are equal to begin and end
        positions of the specified scope.
        """
        self.check_patterns(patterns, scope, self.eq_scope)

    def check_eq_single_scope(self, patterns, scope):
        """
        Checks that begin and end positions of region(s)
        found by pattern(s) are equal to begin and end
        positions of the specified scope and no other
        scopes are present in that regions.
        """
        self.check_patterns(patterns, scope, self.eq_single_scope)

    def check_no_scope(self, patterns, scope):
        """
        Checks that region(s) found by pattern(s) doesn't/don't
        contain subregions with the specified scope.
        """
        self.check_patterns(patterns, scope, self.no_scope)

    # ------------------------------------------------------

    def check_patterns(self, patterns, scope, check):
        if type(patterns) is not list:
            patterns = [ patterns ]
        for pattern in patterns:
            self.check_pattern(pattern, scope, check)

    def check_pattern(self, pattern, scope, check):
        regions = self.view.find_all(pattern)
        self.assertTrue(regions, 'Cannot find pattern /{}/'.format(pattern))
        for region in regions:
            result = check(region, scope)
            self.assertTrue(result.passed(),
                'Text "{}" at line {} found by /{}/ {}'.format(
                    self.text(region),
                    self.view.rowcol(region.begin())[0] + 1,
                    pattern,
                    result.reason()
                    )
                )

    def in_scope(self, region, scope):
        scope_region = self.scopes().find_first(scope, region);
        if scope_region.empty():
            return CheckFailed('should be in scope "{}" but no such scope found'.format(scope))
        if not scope_region.contains(region):
            return CheckFailed(
                'should be in scope "{}" but that scope covers only "{}"'.format(
                    scope, self.text(scope_region)
                ))
        return CheckPassed()

    def in_single_scope(self, region, scope):
        if self.scopes().number_of_scopes(region) != 1:
            return CheckFailed('should have single scope "{}" but multiple scopes found'.format(scope))
        return self.in_scope(region, scope)

    def eq_scope(self, region, scope):
        scope_region = self.scopes().find_first(scope, region);
        if scope_region.empty():
            return CheckFailed('should have scope "{}" but no such scope found'.format(scope))
        if scope_region != region:
            return CheckFailed(
                'should have scope "{}" but that scope covers different region "{}"'.format(
                scope, self.text(scope_region)
                ))
        return CheckPassed()

    def eq_single_scope(self, region, scope):
        if self.scopes().number_of_scopes(region) != 1:
            return CheckFailed('should have single scope "{}" but multiple scopes found'.format(scope))
        return self.eq_scope(region, scope)

    def no_scope(self, region, scope):
        scope_region = self.scopes().find_first(scope, region);
        if not scope_region.empty():
            rowcol = self.view.rowcol(scope_region.begin())
            return CheckFailed('should not have scope "{}" but it was found at line {} column {}'.format(
                scope, rowcol[0], rowcol[1]
                ))
        return CheckPassed()

    def scopes(self):
        if not self._scopes:
            self._scopes = Scopes(self.view)
        return self._scopes

    def reset_scopes(self):
        self._scopes = None

    def text(self, region):
        s = self.view.substr(region)
        return (s
            .replace('\n', r'\n')
            .replace('\r', r'\r')
            .replace('\t', r'\t')
            )     


class Scopes:
    EMPTY_REGION = sublime.Region(0,0)

    def __init__(self, view):
        self.scopes = self._make_scopes_list(view)

    def find_first(self, scope_prefix, region):
        scopes = self._find_by_region(region)
        for scope in scopes:
            if scope['name'].startswith(scope_prefix):
                return scope['region']
        return self.EMPTY_REGION

    def number_of_scopes(self, region):
        return len(list(self._find_by_region(region)))

    def _find_by_region(self, region):
        return filter(lambda scope: (
            scope['region'].intersects(region)
            ), self.scopes)

    @staticmethod
    def _make_scopes_list(view):
        scopes = []
        begin = dict()
        open_scopes = set()
        for pos in range(0, view.size()):
            pos_scopes = set(view.scope_name(pos).split())
            ended_scopes = open_scopes.difference(pos_scopes)
            new_scopes = pos_scopes.difference(open_scopes)

            for scope in new_scopes:
                begin[scope] = pos

            for scope in ended_scopes:
                scopes.append({
                    'name': scope,
                    'region': sublime.Region(begin[scope],pos)
                })

            open_scopes = pos_scopes

        for scope in open_scopes:
            scopes.append({
                'name': scope,
                'region': sublime.Region(begin[scope],view.size())
            })

        return scopes


class CheckResult:
    def __init__(self, passed, reason = None):
        self._passed = passed
        self._reason = reason
    def passed(self): return self._passed
    def reason(self): return self._reason


class CheckFailed(CheckResult):
    def __init__(self, reason):
        super().__init__(False, reason)


class CheckPassed(CheckResult):
    def __init__(self):
        super().__init__(True)
