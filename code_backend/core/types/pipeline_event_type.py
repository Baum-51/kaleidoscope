from enum import StrEnum

class PipelineEventType(StrEnum):
    INPUT_NEW_FRAME = "input_new_frame"
    ALL_FINISHED_DATA = "all_finished_data"