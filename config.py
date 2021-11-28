import os

# For secret string use command :  py -c "import os; print(os.urandom(16))"
class Config(object):
    # Session file shouldn't alter
    SECRET_KEY = os.environ.get('SECRET_KEY') or "b'\xec\x06M\xbd+?\xd3\xd8\x1a\xadB\x91\x02\x16\x14:'"

    MONGODB_SETTINGS = {"db" : "MSWeb"}
    