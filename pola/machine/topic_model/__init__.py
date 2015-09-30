from pola.machine.topic_model.document import Document

def _check_package(name):
    from importlib import util
    spec = util.find_spec(name)
    return True if spec else False

if _check_package("pymc"):
    from pola.machine.topic_model.topic_model import TopicModel

if _check_package("gensim"):
    from pola.machine.topic_model.gtopic_model import GTopicModel

del _check_package
