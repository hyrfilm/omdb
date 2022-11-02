from . import messages

__all__ = ['ALTERNATIVE_CONTENT_TYPES',
           'CONTENT_TYPE',
           'encode_message',
           'decode_message',
          ]

CONTENT_TYPE = 'application/octet-stream'
ALTERNATIVE_CONTENT_TYPES = []

def encode_message(message):
  """Encode Message instance to bytes.

  Args:
    Message instance to encode in to bytes.

  Returns:
    Bytes encoding of Message instance.

  Raises:
    messages.ValidationError if message is not initialized.
  """
  message.check_initialized()
  
  for field in message.all_fields():
    if field and isinstance(field, messages.BytesField):
      return message.get_assigned_value(field.name)

  return b''

def decode_message(message_type, encoded_message):
  """Decode bytes to Message instance.

  Args:
    message_type: Message type to decode data to.
    encoded_message: Encoded version of message as string.

  Returns:
    Decoded instance of message_type.

  Raises:
    DecodeError if an error occurs during decoding.
    messages.ValidationError if merged message is not initialized.
  """
  message = message_type()

  for field in message.all_fields():
    if field and isinstance(field, messages.BytesField):
      setattr(message, field.name, encoded_message)
      message.check_initialized()
      return message

  raise messages.EncodeError('Found no bytes field to decode')
