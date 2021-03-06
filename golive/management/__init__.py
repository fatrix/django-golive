from django.core.management import BaseCommand
from optparse import make_option
from fabric.state import output
import sys
from golive.stacks.stack import StackFactory
import yaml


class CoreCommand(BaseCommand):
    env_id = '<env_id>'
    help = 'Manage the given environment'
    output['stdout'] = False

    def get_config_value(self, key):
        return self.config[key]

    def handle(self, *args, **options):
        job = sys.argv[1]
        if len(args) < 1:
            self.stderr.write('Missing env_id\n')
            sys.exit(1)

        # load user config
        environment_configfile = open("golive.yml", 'r')
        stackname = self.environment_config_temp = yaml.load(environment_configfile)['CONFIG']['STACK']

        self.stack = StackFactory.get(stackname)
        self.stack.setup_environment(args[0])

        # put command options onto stack
        self.stack.options = options

        # task decision
        task = None
        if 'task' in options:
            task = options['task']
        # role decision
        role = None
        if 'role' in options.keys():
            role = options['role']
        # host decision
        host = None
        if 'host' in options.keys():
            host = options['host']

        self.stack._set_stack_config()

        self.stack._cleanout_host(host)
        if task:
            self.stack._cleanout_tasks(task)
        if role:
            self.stack._cleanout_role(role)

        # execute
        self.stack.do(job, task=task, role=role, host=host)

    def end(self):
        self.stdout.write('Done\n')


class SelectiveCommand(CoreCommand):
    pass
    option_list = BaseCommand.option_list + (
        make_option('--task',
                    action='store',
                    dest='task',
                    default=None,
                    help='Execute task'),
        make_option('--role',
                    action='store',
                    dest='role',
                    default=None,
                    help='Run on role'),
        make_option('--host',
                    action='store',
                    dest='host',
                    default=None,
                    help='Operate on host'),
    )
