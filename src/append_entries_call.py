import ast

class AppendEntriesCall:
    def __init__(self, previous_index, previous_term, entries):
        self.previous_index = previous_index
        self.previous_term = previous_term
        self.entries = entries

    def to_message(self):
        return "append_entries after " +\
                str(self.previous_index) + " " + \
               str(self.previous_term) + " @" + \
               str(self.entries)

    @classmethod
    def from_message(cls, message):
        context, entries_as_string = message.split("@")
        previous_info = context.replace("append_entries after ", "").split(" ")
        index, term = int(previous_info[0]), int(previous_info[1])
        entries = ast.literal_eval(entries_as_string)

        return AppendEntriesCall(
            previous_index=index,
            previous_term= term,
            entries=entries
        )
