from dataclasses import field
from typing import Callable, List
from .interop import *


class Events:
    _instance = None
    _connection_state_listeners: List[Callable[[UwConnectionStateEnum], None]] = []
    _game_state_listeners: List[Callable[[UwGameStateEnum], None]] = []
    _update_listeners: List[Callable[[bool], None]] = []
    _shootings_listeners: List[Callable[[UwShootingsArray], None]] = []
    _force_eliminated_listeners: List[Callable[[int], None]] = []
    _chat_listeners: List[Callable[[str, int, UwChatTargetFlags], None]] = []
    _map_state_listeners: List[Callable[[UwMapStateEnum], None]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> None:
        uw_interop.uwSetExceptionCallback(self._exception_callback)
        # uw_interop.uwSetLogCallback(self._log_callback)
        uw_interop.uwSetConnectionStateCallback(self._connection_state_callback)
        uw_interop.uwSetGameStateCallback(self._game_state_callback)
        uw_interop.uwSetUpdateCallback(self._update_callback)
        uw_interop.uwSetShootingsCallback(self._shootings_callback)
        uw_interop.uwSetForceEliminatedCallback(self._force_eliminated_callback)
        uw_interop.uwSetChatCallback(self._chat_callback)
        uw_interop.uwSetTaskCompletedCallback(self._task_completed_callback)
        uw_interop.uwSetMapStateCallback(self._map_state_callback)

    # ---------------------

    def on_connection_state(
        self, listener: Callable[[UwConnectionStateEnum], None]
    ) -> None:
        self._connection_state_listeners.append(listener)

    def on_game_state(self, listener: Callable[[UwGameStateEnum], None]) -> None:
        self._game_state_listeners.append(listener)

    def on_update(self, listener: Callable[[bool], None]) -> None:
        self._update_listeners.append(listener)

    def on_shootings(self, listener: Callable[[UwShootingsArray], None]) -> None:
        self._shootings_listeners.append(listener)

    def on_force_eliminated(self, listener: Callable[[int], None]) -> None:
        self._force_eliminated_listeners.append(listener)

    def on_chat(self, listener: Callable[[str, int, UwChatTargetFlags], None]) -> None:
        self._chat_listeners.append(listener)

    def on_map_state(self, listener: Callable[[UwMapStateEnum], None]) -> None:
        self._map_state_listeners.append(listener)

    # ---------------------

    def _exception_callback(self, message: str) -> None:
        print(f"exception: {message}")
        breakpoint()

    def _connection_state_callback(self, state: UwConnectionStateEnum) -> None:
        for listener in self._connection_state_listeners:
            listener(state)

    def _game_state_callback(self, state: UwGameStateEnum) -> None:
        for listener in self._game_state_listeners:
            listener(state)

    def _update_callback(self, stepping: bool) -> None:
        for listener in self._update_listeners:
            listener(stepping)

    def _shootings_callback(self, data: UwShootingsArray) -> None:
        for listener in self._shootings_listeners:
            listener(data)

    def _force_eliminated_callback(self, force: int) -> None:
        for listener in self._force_eliminated_listeners:
            listener(force)

    def _chat_callback(
        self, message: str, sender: int, flags: UwChatTargetFlags
    ) -> None:
        for listener in self._chat_listeners:
            listener(message, sender, flags)

    def _task_completed_callback(
        self, task_user_data: int, type: UwTaskTypeEnum
    ) -> None:
        pass  # todo

    def _map_state_callback(self, state: UwMapStateEnum) -> None:
        for listener in self._map_state_listeners:
            listener(state)


uw_events = Events()
