from django.conf import settings

from services.managers.util.ts3 import TS3Server


class Teamspeak3Manager:
    def __init__(self):
        pass

    @staticmethod
    def __get_created_server():
        server = TS3Server(settings.TEAMSPEAK3_SERVER_IP, settings.TEAMSPEAK3_SERVER_PORT)
        server.login(settings.TEAMSPEAK3_SERVERQUERY_USER, settings.TEAMSPEAK3_SERVERQUERY_PASSWORD)
        server.use(settings.TEAMSPEAK3_VIRTUAL_SERVER)
        return server

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized

    @staticmethod
    def __generate_username(username, corp_ticker):
        return "[" + corp_ticker + "]" + username

    @staticmethod
    def __generate_username_blue(username, corp_ticker):
        return "[BLUE][" + corp_ticker + "]" + username

    @staticmethod
    def _get_userid(uid):
        server = Teamspeak3Manager.__get_created_server()
        ret = server.send_command('customsearch', {'ident': 'sso_uid', 'pattern': uid})
        if ret and 'keys' in ret and 'cldbid' in ret['keys']:
            return ret['keys']['cldbid']

    @staticmethod
    def _group_id_by_name(groupname):
        server = Teamspeak3Manager.__get_created_server()
        group_cache = server.send_command('servergrouplist')

        for group in group_cache:
            if group['keys']['name'] == groupname:
                return group['keys']['sgid']

        return None

    @staticmethod
    def _create_group(groupname):
        server = Teamspeak3Manager.__get_created_server()
        sgid = Teamspeak3Manager._group_id_by_name(groupname)
        if not sgid:
            ret = server.send_command('servergroupadd', {'name': groupname})
            Teamspeak3Manager.__group_cache = None
            sgid = ret['keys']['sgid']
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_modify_power', 'permvalue': 75,
                                 'permnegated': 0, 'permskip': 0})
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_member_add_power', 'permvalue': 100,
                                 'permnegated': 0, 'permskip': 0})
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_member_remove_power', 'permvalue': 100,
                                 'permnegated': 0, 'permskip': 0})
        return sgid

    @staticmethod
    def _user_group_list(cldbid):
        server = Teamspeak3Manager.__get_created_server()
        groups = server.send_command('servergroupsbyclientid', {'cldbid': cldbid})
        outlist = {}

        if type(groups) == list:
            for group in groups:
                outlist[group['keys']['name']] = group['keys']['sgid']
        elif type(groups) == dict:
            outlist[groups['keys']['name']] = groups['keys']['sgid']

        return outlist

    @staticmethod
    def _group_list():
        server = Teamspeak3Manager.__get_created_server()
        group_cache = server.send_command('servergrouplist')
        outlist = {}
        if group_cache:
            for group in group_cache:
                outlist[group['keys']['name']] = group['keys']['sgid']
        else:
            print '1024 error'

        return outlist

    @staticmethod
    def _add_user_to_group(uid, groupname):
        groupname = groupname[:30]
        server = Teamspeak3Manager.__get_created_server()
        server_groups = Teamspeak3Manager._group_list()
        user_groups = Teamspeak3Manager._user_group_list(uid)

        if not groupname in server_groups:
            Teamspeak3Manager._create_group(groupname)
        if not groupname in user_groups:
            server.send_command('servergroupaddclient',
                                {'sgid': Teamspeak3Manager._group_id_by_name(groupname), 'cldbid': uid})

    @staticmethod
    def _remove_user_from_group(uid, groupname):
        groupname = groupname[:30]
        server = Teamspeak3Manager.__get_created_server()
        server_groups = Teamspeak3Manager._group_list()
        user_groups = Teamspeak3Manager._user_group_list(uid)

        if groupname in server_groups:
            Teamspeak3Manager._create_group(groupname)
        if groupname in user_groups:
            server.send_command('servergroupdelclient',
                                {'sgid': Teamspeak3Manager._group_id_by_name(groupname), 'cldbid': uid})

    @staticmethod
    def add_user(username, corp_ticker):
        username_clean = Teamspeak3Manager.__generate_username(Teamspeak3Manager.__santatize_username(username),
                                                               corp_ticker)
        server = Teamspeak3Manager.__get_created_server()
        token = ""

        server_groups = Teamspeak3Manager._group_list()

        if not settings.DEFAULT_ALLIANCE_GROUP in server_groups:
            Teamspeak3Manager._create_group(settings.DEFAULT_ALLIANCE_GROUP)

        alliance_group_id = Teamspeak3Manager._group_id_by_name(settings.DEFAULT_ALLIANCE_GROUP)

        ret = server.send_command('tokenadd', {'tokentype': 0, 'tokenid1': alliance_group_id, 'tokenid2': 0,
                                               'tokendescription': username_clean,
                                               'tokencustomset': "ident=sso_uid value=%s" % username_clean})

        try:
            if 'keys' in ret:
                if 'token' in ret['keys']:
                    token = ret['keys']['token']
        except:
            pass

        return username_clean, token

    @staticmethod
    def add_blue_user(username, corp_ticker):
        username_clean = Teamspeak3Manager.__generate_username_blue(Teamspeak3Manager.__santatize_username(username),
                                                                    corp_ticker)
        server = Teamspeak3Manager.__get_created_server()
        token = ""

        server_groups = Teamspeak3Manager._group_list()
        if not settings.DEFAULT_BLUE_GROUP in server_groups:
            Teamspeak3Manager._create_group(settings.DEFAULT_BLUE_GROUP)

        blue_group_id = Teamspeak3Manager._group_id_by_name(settings.DEFAULT_BLUE_GROUP)

        ret = server.send_command('tokenadd', {'tokentype': 0, 'tokenid1': blue_group_id, 'tokenid2': 0,
                                               'tokendescription': username_clean,
                                               'tokencustomset': "ident=sso_uid value=%s" % username_clean})

        try:
            if 'keys' in ret:
                if 'token' in ret['keys']:
                    token = ret['keys']['token']

        except:
            pass

        return username_clean, token

    @staticmethod
    def delete_user(uid):
        server = Teamspeak3Manager.__get_created_server()
        user = Teamspeak3Manager._get_userid(uid)
        if user:
            for client in server.send_command('clientlist'):
                if client['keys']['client_database_id'] == user:
                    server.send_command('clientkick', {'clid': client['keys']['clid'], 'reasonid': 5,
                                                       'reasonmsg': 'Auth service deleted'})

            ret = server.send_command('clientdbdelete', {'cldbid': user})
            if ret == '0':
                return True
        else:
            return True

    @staticmethod
    def check_user_exists(uid):
        if Teamspeak3Manager._get_userid(uid):
            return True

        return False

    @staticmethod
    def generate_new_permissionkey(uid, username, corpticker):
        Teamspeak3Manager.delete_user(uid)
        return Teamspeak3Manager.add_user(username, corpticker)

    @staticmethod
    def generate_new_blue_permissionkey(uid, username, corpticker):
        Teamspeak3Manager.delete_user(uid)
        return Teamspeak3Manager.add_blue_user(username, corpticker)

    @staticmethod
    def update_groups(uid, l_groups):
        print uid
        print l_groups
        userid = Teamspeak3Manager._get_userid(uid)
        if userid is not None:
            server_groups = Teamspeak3Manager._group_list()
            user_groups = set(Teamspeak3Manager._user_group_list(userid))
            groups = []
            for l_group in l_groups:
                groups.append(l_group[:30])

            act_groups = set([g.replace(' ', '-') for g in groups])
            addgroups = act_groups - user_groups
            remgroups = user_groups - act_groups

            print userid
            print addgroups
            print remgroups

            for g in addgroups:
                if not g in server_groups.keys():
                    Teamspeak3Manager._create_group(g)
                Teamspeak3Manager._add_user_to_group(userid, g)

            for g in remgroups:
                Teamspeak3Manager._remove_user_from_group(userid, g)

