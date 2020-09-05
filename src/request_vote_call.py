
class RequestVoteCall:
    def __init__(self, for_term, latest_log_index, latest_log_term):
        self.for_term = for_term
        self.latest_log_index = latest_log_index
        self.latest_log_term = latest_log_term

    def to_message(self):
        return "can_I_count_on_your_vote_in_term " \
                + str(self.for_term) \
                + " ? " \
                + "last_log_entry: " \
                + str(self.latest_log_index) \
                + " " \
                + str(self.latest_log_term)

    @classmethod
    def from_message(cls, message):
        numeric_markers = message.replace("can_I_count_on_your_vote_in_term ", "").split(" ")
        current_term, index, latest_log_term = int(numeric_markers[0]), int(numeric_markers[3]), int(numeric_markers[4])

        return RequestVoteCall(
            for_term=current_term,
            latest_log_index=index,
            latest_log_term=latest_log_term,
        )
