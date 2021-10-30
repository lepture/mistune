from mistune import Markdown, AstRenderer, HTMLRenderer, plugins
from tests import BaseTestCase, fixtures
import pprint

def load_plugin(plugin_name, ast=False):
    _plugin = getattr(plugins, "plugin_{}".format(plugin_name))

    class TestPlugin(BaseTestCase):
        md = Markdown(renderer=HTMLRenderer(escape=False), plugins=[_plugin])

    def test_ast_renderer(self):
        """ Test the AST JSON renderer. This shows up as one test in the output, so print statements are listed for each phrase processed to help in test verification (output is supressed in most testing contexts, of course). """
        md = Markdown(renderer=AstRenderer(), plugins=[_plugin])
        data = fixtures.load_json(plugin_name + ".json")

        def run_json_phrase(phrase):
            """ Process the test structure loaded from the json test file. Phrase is expected to follow this structure. Either 'no_type' or 'tokens' is required, but not both.
            {
                "text": Required. A string to be processed by the markdown renderer,
                "message": Optional. If provided, a name for the test to be be printed when tests are run verbosely or failure occurs.
                "tokens": If provided, indicates the expected/correct AST that the "text" field should render as.
                "no_type": If provided, indicates a tag that should *not* exist in the AST tree. Use this to ensure that a plugin is not over-eager in rendering things it should not.
            } 
            """
            if 'message' in phrase:
                message = phrase['message']
            else:
                message = phrase['text']

            if 'no_type' in phrase and phrase['no_type']:
                message += f"  (expect no '{phrase['no_type']}' token)"

            # when running pytest in verbose modes, show the subtest name. 
            print("\tRun subtest: " + message)

            # - add more useful debugging information in case the assertion fails
            # This is useful in test development because you do not have to write out 
            # the entire structure for a new test case in advance, you can just add them
            # to the json file, run the test, and then copy the Rendered value (assuming it is correct)
            message =  "\n\n" + message + "\nMarkdown:\n`" + phrase['text'] + "`"
            try:
                message += "\n\n**Markdown Rendered**:\n" + pprint.pformat(md(phrase["text"]), indent=4, width=120).replace("'", '"')
            except Exception as e:
                # this indicates an exception is thrown in the rendering phase itself.
                # so we add it to the message - it is useful for debugging to have the complete message written before the exception is really thrown  
                message += f"\n\nAttempting to render markdown fails with {e}"
            if "tokens" in phrase:
                message += ("\n\n**Expected**:\n" + pprint.pformat(phrase["tokens"], indent=4, width=120).replace("'", '"'))
            
            if 'no_type' in phrase and phrase['no_type']:
                self.assertFalse(find_type(md(phrase["text"]), phrase['no_type']), message)
            else:
                self.assertEqual(md(phrase["text"]), phrase["tokens"], message)

        if type(data) is list:
        
            for phrase in data:
                run_json_phrase(phrase)
        else:
            run_json_phrase(data)

    if ast:
        test_ast_renderer.__doc__ = "Run {} ast renderer".format(plugin_name)
        setattr(TestPlugin, "test_ast_renderer", test_ast_renderer)

    TestPlugin.load_fixtures(plugin_name + ".txt")
    globals()["TestPlugin_" + plugin_name] = TestPlugin

def find_type(ref, objtype):
    """ Analyze the ref AST to see if any types exist inside.
    
    Args:
        ref (dict): an AST
        objtype (str): A type name to search for in the nested AST.
    
    Returns: 
        bool: True if the type exists anywhere in the AST, False otherwise.
    """
    if type(ref) is list:
        for subref in ref:
            if find_type(subref, objtype):
                return(True)
    elif type(ref) is dict:
        if objtype == ref['type']:
            return(True)
        return(find_type(ref.values(), objtype))
    return(False)

load_plugin("url")
load_plugin("strikethrough")
load_plugin("footnotes", True)
load_plugin("table", True)
load_plugin("task_lists", True)
load_plugin("def_list", True)
load_plugin("abbr", True)
load_plugin('mathblock', True)
load_plugin('mathspan', True)
