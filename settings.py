import os

'''В этом файле мы храним значения, необходимые для работы с tg и с базами данных. 
На работе я использовал os и отдельный файл для хранения личных данных, он так же передается в докер и личные данные не появляются в общем доступе.
В этом проекте я решил не реализовывать такую передачу.'''

API_ID = "22543134"
API_HASH = "c885f8546d67197050688eff7e499e70"
BOT_TOKEN = "6859624515:AAFXPT9BXueK80OB6Ggkyyd4EovFFDG39L4"

# DATABASE_URL = "postgresql://postgres:pwdmaxbit@localhost:5432/postgres"

DATABASE_URL = "postgresql://habrpguser:pgpwd4habr@postgres:5432/habrdb"