# 📚 MSG_RECEIVER

import json
from typing import Optional

from PW_UTILS.LOG import LOG
from PW_UTILS.UTILS import UTILS
from .MSG import MSG


class MSG_RECEIVER:
    """Lightweight message receiver for inbox-like endpoints.

    Responsibilities:
    - Parse incoming events
    - Validate headers (and optionally signatures)
    - Execute a handler with the envelope
    """

    def __init__(self):
        self._timer = UTILS.Timer()

    def _elapsed(self):
        return self._timer.Elapsed()

    def _parse(self, event: dict[str, any]) -> dict[str, any]:
        UTILS.Require(event)

        envelope = {}
        if 'httpMethod' not in event:
            envelope = event
        elif 'body' in event and event['body'] is not None:
            envelope = json.loads(event['body'])
        elif event['httpMethod'] == 'GET':
            envelope = {}

        return envelope

    def _validate(
        self,
        msg: MSG,
        speed: dict[str, any],
        expected_to: Optional[str] = None,
        validator: Optional[object] = None,
        public_key: Optional[str] = None,
        public_key_provider: Optional[object] = None,
        ignore_validation: bool = False,
    ) -> dict[str, any]:
        error = None
        checks: list[str] = []

        try:
            msg.VerifyHeader()
            checks.append('Header ok')

            if expected_to is not None:
                UTILS.AssertEqual(
                    given=msg.RequireTo().lower(),
                    expect=expected_to.lower(),
                    msg=f'Wrong domain. Expected [{expected_to}], but received [{msg.RequireTo()}]!')
                checks.append('Recipient ok')

            if not ignore_validation:
                if public_key_provider is not None and public_key is None:
                    public_key = public_key_provider(msg)

                if validator is not None:
                    started = self._timer.StartWatch()
                    msg.VerifySignature(public_key=public_key, validator=validator)
                    checks.append('Signature ok')
                    speed['Verify signature'] = self._timer.StopWatch(started)

        except Exception as exc:
            if hasattr(exc, 'message'):
                error = f'{exc.message}'
            else:
                error = f'{exc}'

        return {
            'Error': error,
            'Checks': checks,
        }

    def _execute(self, validation: dict[str, any], envelope: dict[str, any], handler: object = None) -> dict[str, any]:
        if validation['Error']:
            return {
                'Result': 'Ignored, invalid envelope!'
            }

        if handler is None:
            return {
                'Result': 'No handler'
            }

        answer = handler(envelope)
        return {
            'Result': 'Executed',
            'Answer': answer,
        }

    def Handle(
        self,
        event: dict[str, any],
        handler: object = None,
        expected_to: Optional[str] = None,
        validator: Optional[object] = None,
        public_key: Optional[str] = None,
        public_key_provider: Optional[object] = None,
        ignore_validation: bool = False,
    ) -> dict[str, any]:
        LOG.Print(f'📮 MSG_RECEIVER.Handle():', event)

        UTILS.Require(event)
        envelope = self._parse(event)
        LOG.Print(f'📮 MSG_RECEIVER.Handle:', 'envelope=', envelope)

        if envelope == {}:
            return {
                'Result': 'Inbox is working :)'
            }

        speed: dict[str, any] = {}
        started = self._timer.StartWatch()
        msg = MSG(envelope)

        validation = self._validate(
            msg=msg,
            speed=speed,
            expected_to=expected_to,
            validator=validator,
            public_key=public_key,
            public_key_provider=public_key_provider,
            ignore_validation=ignore_validation,
        )
        execution = self._execute(validation, envelope, handler)
        speed['Total handling'] = self._timer.StopWatch(started)

        output = execution if execution is not None else {}
        if isinstance(output, dict):
            output['Insights'] = {
                'Speed': speed,
                'Validation': validation,
                'Received': envelope,
            }

        if validation['Error']:
            output['Error'] = validation['Error']

        return output
