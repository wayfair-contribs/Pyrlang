from __future__ import absolute_import
from __future__ import print_function

from Pyrlang import term, gen
from Pyrlang.process import Process
from Pyrlang.node import Node


class Rex(Process):
    """ Remote executor for RPC calls. Registers itself under the name ``rex``
        and accepts RPC call messages.
        Erlang ``rpc:call`` sends a ``$gen_call`` styled message to the
        registered name ``rex`` on the remote node which we parse and attempt
        to execute.
    """

    def __init__(self, node: Node) -> None:
        Process.__init__(self, node)
        node.register_name(self, term.Atom('rex'))

    def handle_one_inbox_message(self, msg) -> None:
        """ Function overrides ``Process.handle_one_inbox_message`` and expects
            a ``$gen_call`` styled message.
            The result or exception are delivered back to the sender via
            message passing.

        :param msg: A tuple with Atom ``$gen_call`` as the first element
        :return: None
        """
        gencall = gen.parse_gen_call(msg)
        if isinstance(gencall, str):
            print("REX:", gencall)
            return

        # Find and run the thing
        try:
            pmod = __import__(gencall.get_mod_str(), fromlist=[''])
            pfun = getattr(pmod, gencall.get_fun_str())
            args = gencall.get_args()

            # Call the thing
            val = pfun(*args)
            # Send a reply
            gencall.reply(local_pid=self.pid_,
                          result=(gencall.ref_, val))

        except Exception as excpt:
            # Send an error
            gencall.reply_exit(local_pid=self.pid_,
                               reason=excpt)


__all__ = ['Rex']
