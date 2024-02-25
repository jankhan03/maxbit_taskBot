
'''В этом файле мы создадим класс состояний, для работы с FSM'''

class UserState:
    def __init__(self):
        self.user_states = {}
        self.user_data = {}

    def set_state(self, user_id, state):
        self.user_states[user_id] = state

    def get_state(self, user_id):
        return self.user_states.get(user_id, None)

    def delete_state(self, user_id):
        if user_id in self.user_states:
            del self.user_states[user_id]

    def set_data(self, user_id, key, value):
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id][key] = value

    def get_data(self, user_id, key):
        return self.user_data.get(user_id, {}).get(key, None)

    def delete_data(self, user_id):
        if user_id in self.user_data:
            del self.user_data[user_id]