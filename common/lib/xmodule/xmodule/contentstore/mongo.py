# -*- coding: utf-8 -*-
"""
MongoDB/GridFS-level code for the contentstore.
"""
import os
import json
import pymongo
import gridfs
from gridfs.errors import NoFile
from fs.osfs import OSFS
from bson.son import SON

from mongodb_proxy import autoretry_read
from opaque_keys.edx.keys import AssetKey
from xmodule.contentstore.content import XASSET_LOCATION_TAG
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.django import ASSET_IGNORE_REGEX
from xmodule.util.misc import escape_invalid_characters
from xmodule.mongo_utils import connect_to_mongodb, create_collection_index
from .content import StaticContent, ContentStore, StaticContentStream


class MongoContentStore(ContentStore):
    """
    MongoDB-backed ContentStore.
    """

    # pylint: disable=unused-argument, bad-continuation
    def __init__(
            self, host, db,
            port=27017, tz_aware=True, user=None, password=None, bucket='fs', collection=None, **kwargs
    ):
        """
        Establish the connection with the mongo backend and connect to the collections

        :param collection: ignores but provided for consistency w/ other doc_store_config patterns
        """
        # GridFS will throw an exception if the Database is wrapped in a MongoProxy. So don't wrap it.
        # The appropriate methods below are marked as autoretry_read - those methods will handle
        # the AutoReconnect errors.
        proxy = False
        mongo_db = connect_to_mongodb(
            db, host,
            port=port, tz_aware=tz_aware, user=user, password=password, proxy=proxy, **kwargs
        )

        self.fs = gridfs.GridFS(mongo_db, bucket)  # pylint: disable=invalid-name

        self.fs_files = mongo_db[bucket + ".files"]  # the underlying collection GridFS uses
        self.chunks = mongo_db[bucket + ".chunks"]

    def close_connections(self):
        """
        Closes any open connections to the underlying databases
        """
        self.fs_files.database.connection.close()

    def _drop_database(self, database=True, collections=True, connections=True):
        """
        A destructive operation to drop the underlying database and close all connections.
        Intended to be used by test code for cleanup.

        If database is True, then this should drop the entire database.
        Otherwise, if collections is True, then this should drop all of the collections used
        by this modulestore.
        Otherwise, the modulestore should remove all data from the collections.

        If connections is True, then close the connection to the database as well.
        """
        connection = self.fs_files.database.connection

        if database:
            connection.drop_database(self.fs_files.database)
        elif collections:
            self.fs_files.drop()
            self.chunks.drop()
        else:
            self.fs_files.remove({})
            self.chunks.remove({})

        if connections:
            self.close_connections()

    def save(self, content):
        content_id, content_son = self.asset_db_key(content.location)

        # The way to version files in gridFS is to not use the file id as the _id but just as the filename.
        # Then you can upload as many versions as you like and access by date or version. Because we use
        # the location as the _id, we must delete before adding (there's no replace method in gridFS)
        self.delete(content_id)  # delete is a noop if the entry doesn't exist; so, don't waste time checking

        thumbnail_location = content.thumbnail_location.to_deprecated_list_repr() if content.thumbnail_location else None
        with self.fs.new_file(_id=content_id, filename=unicode(content.location), content_type=content.content_type,
                              displayname=content.name, content_son=content_son,
                              thumbnail_location=thumbnail_location,
                              import_path=content.import_path,
                              # getattr b/c caching may mean some pickled instances don't have attr
                              locked=getattr(content, 'locked', False)) as fp:
            if hasattr(content.data, '__iter__'):
                for chunk in content.data:
                    fp.write(chunk)
            else:
                fp.write(content.data)

        return content

    def delete(self, location_or_id):
        """
        Delete an asset.
        """
        if isinstance(location_or_id, AssetKey):
            location_or_id, _ = self.asset_db_key(location_or_id)
        # Deletes of non-existent files are considered successful
        self.fs.delete(location_or_id)

    ''' kmooc MME '''

    def save_cdn(self, content):
        '''
        CDN MME
        :param content:
        :return:
        '''
        content_id, content_son = self.asset_db_key(content.location)
        self.delete(content_id)

        try:
            uuid = unicode(content['uuid'])
        except:
            # pass
            uuid = unicode(content.uuid)

        try:
            playtime = unicode(content['playtime'])
        except:
            # pass
            playtime = unicode(content.playtime)

        with self.fs.new_file(_id=content_id,
                              filename=unicode(content.location),
                              displayname=content.name,
                              content_son=content_son,
                              cdn_url=content.cdn_url,
                              content_type=content.content_type,
                              thumbnail_location=None,
                              uuid=uuid, state=unicode(content.state), playtime=playtime,
                              thumbnail_url=unicode(content.thumbnail_url),
                              locked=getattr(content, 'locked', False)
                              ) as fp:

            print("mongodb insert ok: %s, %s, %s" % (uuid, playtime, content.location))

        return content

    def update_state(self, uuid, state):

        ##todo update 테스트를 해야함
        ## db.fs.files.find({contentType: '^video/mp4$'})
        ## db.fs.files.find({_id: 'asset-v1:edX+DemoX+Demo_Course+type@cdn+block@녹화_2016_03_11_15_10_10_264.mp4'})

        # asset_db_key, __ = self.asset_db_key(location)

        with self.fs.update({'uuid': uuid}, {'state': state}, upsert=True) as fp:
            print "CDN update os: %s, %s" % (uuid, state)

    def find_cdn(self, location, throw_on_not_found=True, as_stream=False):
        '''
        CDN MME
        :param location:
        :param throw_on_not_found:
        :param as_stream:
        :return:
        '''
        content_id, __ = self.asset_db_key(location)

        try:
            with self.fs.get(content_id) as fp:
                if as_stream:
                    return StaticContentStream(
                        content_id, fp.displayname, fp.content_type, fp.read(), last_modified_at=fp.uploadDate
                    )
                return StaticContent(
                    content_id, fp.displayname, fp.content_type, fp.read(), last_modified_at=fp.uploadDate,
                )
        except NoFile:
            if throw_on_not_found:
                raise NotFoundError(content_id)
            else:
                return None

    def find_cdn_uuid(self, location, throw_on_not_found=True, as_stream=False):
        '''
        KMOOC UUID find
        Args:
            location:
            throw_on_not_found:
            as_stream:

        Returns:

        '''
        content_id, __ = self.asset_db_key(location)
        try:
            with self.fs.get(content_id) as fp:
                return {'uuid': fp.uuid, 'playtime': fp.playtime, 'cdn_url': fp.cdn_url}


        except NoFile:
            if throw_on_not_found:
                raise NotFoundError(content_id)
            else:
                return None

    def delete_cdn(self, location_or_id):
        '''
        CDN MME
        todo MME DELETE Call 처리
        :param location_or_id:
        :return:
        '''
        if isinstance(location_or_id, AssetKey):
            location_or_id, _ = self.asset_db_key(location_or_id)
        # Deletes of non-existent files are considered successful
        self.fs.delete(location_or_id)

    def get_all_cdn_content_for_course(self, course_key, start=0, maxresults=-1, sort=None, filter_params=None):
        ''' kmooc mme '''
        return self._get_all_cdn_content_for_course(
            course_key, start=start, maxresults=maxresults, get_thumbnails=False, sort=sort, filter_params=filter_params
        )

    def _get_all_cdn_content_for_course(self,
                                        course_key,
                                        get_thumbnails=False,
                                        start=0,
                                        maxresults=-1,
                                        sort=None,
                                        filter_params=None):
        ''' kmooc MME '''

        '''
        Returns a list of all static assets for a course. The return format is a list of asset data dictionary elements.

        The asset data dictionaries have the following keys:
            asset_key (:class:`opaque_keys.edx.AssetKey`): The key of the asset
            displayname: The human-readable name of the asset
            uploadDate (datetime.datetime): The date and time that the file was uploadDate
            contentType: The mimetype string of the asset
            md5: An md5 hash of the asset content
        '''
        query = query_for_course(course_key, "cdn" if not get_thumbnails else "thumbnail")
        find_args = {"sort": sort}
        if maxresults > 0:
            find_args.update({
                "skip": start,
                "limit": maxresults,
            })
        if filter_params:
            query.update(filter_params)

        items = self.fs_files.find(query, **find_args)
        count = items.count()

        print "count----------------------D", count

        assets = list(items)

        # import logging;logging.info(assets)

        # We're constructing the asset key immediately after retrieval from the database so that
        # callers are insulated from knowing how our identifiers are stored.
        for asset in assets:
            asset_id = asset.get('content_son', asset['_id'])
            asset['asset_key'] = course_key.make_asset_key(asset_id['category'], asset_id['name'])
        return assets, count

    @autoretry_read()
    def find(self, location, throw_on_not_found=True, as_stream=False):
        content_id, __ = self.asset_db_key(location)

        try:
            if as_stream:
                fp = self.fs.get(content_id)
                thumbnail_location = getattr(fp, 'thumbnail_location', None)
                if thumbnail_location:
                    thumbnail_location = location.course_key.make_asset_key(
                        'thumbnail',
                        thumbnail_location[4]
                    )
                return StaticContentStream(
                    location, fp.displayname, fp.content_type, fp, last_modified_at=fp.uploadDate,
                    thumbnail_location=thumbnail_location,
                    import_path=getattr(fp, 'import_path', None),
                    length=fp.length, locked=getattr(fp, 'locked', False),
                    content_digest=getattr(fp, 'md5', None),
                )
            else:
                with self.fs.get(content_id) as fp:
                    thumbnail_location = getattr(fp, 'thumbnail_location', None)
                    if thumbnail_location:
                        thumbnail_location = location.course_key.make_asset_key(
                            'thumbnail',
                            thumbnail_location[4]
                        )
                    return StaticContent(
                        location, fp.displayname, fp.content_type, fp.read(), last_modified_at=fp.uploadDate,
                        thumbnail_location=thumbnail_location,
                        import_path=getattr(fp, 'import_path', None),
                        length=fp.length, locked=getattr(fp, 'locked', False),
                        content_digest=getattr(fp, 'md5', None),
                    )
        except NoFile:
            if throw_on_not_found:
                raise NotFoundError(content_id)
            else:
                return None

    def export(self, location, output_directory):
        content = self.find(location)

        filename = content.name
        if content.import_path is not None:
            output_directory = output_directory + '/' + os.path.dirname(content.import_path)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Escape invalid char from filename.
        export_name = escape_invalid_characters(name=filename, invalid_char_list=['/', '\\'])

        disk_fs = OSFS(output_directory)

        with disk_fs.open(export_name, 'wb') as asset_file:
            asset_file.write(content.data)

    def export_all_for_course(self, course_key, output_directory, assets_policy_file):
        """
        Export all of this course's assets to the output_directory. Export all of the assets'
        attributes to the policy file.

        Args:
            course_key (CourseKey): the :class:`CourseKey` identifying the course
            output_directory: the directory under which to put all the asset files
            assets_policy_file: the filename for the policy file which should be in the same
                directory as the other policy files.
        """
        policy = {}
        assets, __ = self.get_all_content_for_course(course_key)

        for asset in assets:
            # TODO: On 6/19/14, I had to put a try/except around this
            # to export a course. The course failed on JSON files in
            # the /static/ directory placed in it with an import.
            #
            # If this hasn't been looked at in a while, remove this comment.
            #
            # When debugging course exports, this might be a good place
            # to look. -- pmitros
            self.export(asset['asset_key'], output_directory)
            for attr, value in asset.iteritems():
                if attr not in ['_id', 'md5', 'uploadDate', 'length', 'chunkSize', 'asset_key']:
                    policy.setdefault(asset['asset_key'].block_id, {})[attr] = value

        with open(assets_policy_file, 'w') as f:
            json.dump(policy, f, sort_keys=True, indent=4)

    def get_all_content_thumbnails_for_course(self, course_key):
        return self._get_all_content_for_course(course_key, get_thumbnails=True)[0]

    def get_all_content_for_course(self, course_key, start=0, maxresults=-1, sort=None, filter_params=None):
        return self._get_all_content_for_course(
            course_key, start=start, maxresults=maxresults, get_thumbnails=False, sort=sort, filter_params=filter_params
        )

    def remove_redundant_content_for_courses(self):
        """
        Finds and removes all redundant files (Mac OS metadata files with filename ".DS_Store"
        or filename starts with "._") for all courses
        """
        assets_to_delete = 0
        for prefix in ['_id', 'content_son']:
            query = SON([
                ('{}.tag'.format(prefix), XASSET_LOCATION_TAG),
                ('{}.category'.format(prefix), 'asset'),
                ('{}.name'.format(prefix), {'$regex': ASSET_IGNORE_REGEX}),
            ])
            items = self.fs_files.find(query)
            assets_to_delete = assets_to_delete + items.count()
            for asset in items:
                self.fs.delete(asset[prefix])

            self.fs_files.remove(query)
        return assets_to_delete

    @autoretry_read()
    def _get_all_content_for_course(self,
                                    course_key,
                                    get_thumbnails=False,
                                    start=0,
                                    maxresults=-1,
                                    sort=None,
                                    filter_params=None):
        '''
        Returns a list of all static assets for a course. The return format is a list of asset data dictionary elements.

        The asset data dictionaries have the following keys:
            asset_key (:class:`opaque_keys.edx.AssetKey`): The key of the asset
            displayname: The human-readable name of the asset
            uploadDate (datetime.datetime): The date and time that the file was uploadDate
            contentType: The mimetype string of the asset
            md5: An md5 hash of the asset content
        '''
        # TODO: Using an aggregate() instead of a find() here is a hack to get around the fact that Mongo 3.2 does not
        # support sorting case-insensitively.
        # If a sort on displayname is requested, the aggregation pipeline creates a new field:
        # `insensitive_displayname`, a lowercase version of `displayname` that is sorted on instead.
        # Mongo 3.4 does not require this hack. When upgraded, change this aggregation back to a find and specifiy
        # a collation based on user's language locale instead.
        # See: https://openedx.atlassian.net/browse/EDUCATOR-2221

        pipeline_stages = []
        print "filter_params----------------------D", filter_params
        query = query_for_course(course_key, 'asset' if not get_thumbnails else 'thumbnail')

        if filter_params:
            query.update(filter_params)
        print "query!", query
        pipeline_stages.append({'$match': query})
        print "pipeline_stages", pipeline_stages

        if sort:
            sort = dict(sort)
            if 'displayname' in sort:
                pipeline_stages.append({
                    '$project': {
                        'contentType': 1,
                        'locked': 1,
                        'chunkSize': 1,
                        'content_son': 1,
                        'displayname': 1,
                        'filename': 1,
                        'length': 1,
                        'import_path': 1,
                        'uploadDate': 1,
                        'thumbnail_location': 1,
                        'md5': 1,
                        'insensitive_displayname': {
                            '$toLower': '$displayname'
                        }
                    }
                })
                sort = {'insensitive_displayname': sort['displayname']}
                print "sort", sort
            pipeline_stages.append({'$sort': sort})

        # This is another hack to get the total query result count, but only the Nth page of actual documents
        # See: https://stackoverflow.com/a/39784851/6620612
        pipeline_stages.append({'$group': {'_id': None, 'count': {'$sum': 1}, 'results': {'$push': '$$ROOT'}}})
        if maxresults > 0:
            pipeline_stages.append({
                '$project': {
                    'count': 1,
                    'results': {
                        '$slice': ['$results', start, maxresults]
                    }
                }
            })

        items = self.fs_files.aggregate(pipeline_stages)
        if items['result']:
            result = items['result'][0]
            count = result['count']
            assets = list(result['results'])
        else:
            # no results
            count = 0
            assets = []

        # We're constructing the asset key immediately after retrieval from the database so that
        # callers are insulated from knowing how our identifiers are stored.
        for asset in assets:
            asset_id = asset.get('content_son', asset['_id'])
            asset['asset_key'] = course_key.make_asset_key(asset_id['category'], asset_id['name'])
        return assets, count

    def set_attr(self, asset_key, attr, value=True):
        """
        Add/set the given attr on the asset at the given location. Does not allow overwriting gridFS built in
        attrs such as _id, md5, uploadDate, length. Value can be any type which pymongo accepts.

        Returns nothing

        Raises NotFoundError if no such item exists
        Raises AttributeError is attr is one of the build in attrs.

        :param asset_key: an AssetKey
        :param attr: which attribute to set
        :param value: the value to set it to (any type pymongo accepts such as datetime, number, string)
        """
        self.set_attrs(asset_key, {attr: value})

    def get_attr(self, location, attr, default=None):
        """
        Get the value of attr set on location. If attr is unset, it returns default. Unlike set, this accessor
        does allow getting the value of reserved keywords.
        :param location: a c4x asset location
        """
        return self.get_attrs(location).get(attr, default)

    def set_attrs(self, location, attr_dict):
        """
        Like set_attr but sets multiple key value pairs.

        Returns nothing.

        Raises NotFoundError if no such item exists
        Raises AttributeError is attr_dict has any attrs which are one of the build in attrs.

        :param location:  a c4x asset location
        """
        for attr in attr_dict.iterkeys():
            if attr in ['_id', 'md5', 'uploadDate', 'length']:
                raise AttributeError("{} is a protected attribute.".format(attr))
        asset_db_key, __ = self.asset_db_key(location)
        # catch upsert error and raise NotFoundError if asset doesn't exist
        result = self.fs_files.update({'_id': asset_db_key}, {"$set": attr_dict}, upsert=False)
        if not result.get('updatedExisting', True):
            raise NotFoundError(asset_db_key)

    @autoretry_read()
    def get_attrs(self, location):
        """
        Gets all of the attributes associated with the given asset. Note, returns even built in attrs
        such as md5 which you cannot resubmit in an update; so, don't call set_attrs with the result of this
        but only with the set of attrs you want to explicitly update.

        The attrs will be a superset of _id, contentType, chunkSize, filename, uploadDate, & md5

        :param location: a c4x asset location
        """
        asset_db_key, __ = self.asset_db_key(location)
        item = self.fs_files.find_one({'_id': asset_db_key})
        if item is None:
            raise NotFoundError(asset_db_key)
        return item

    def copy_all_course_assets(self, source_course_key, dest_course_key):
        """
        See :meth:`.ContentStore.copy_all_course_assets`

        This implementation fairly expensively copies all of the data
        """
        source_query = query_for_course(source_course_key)
        # it'd be great to figure out how to do all of this on the db server and not pull the bits over
        for asset in self.fs_files.find(source_query):
            asset_key = self.make_id_son(asset)
            # don't convert from string until fs access
            source_content = self.fs.get(asset_key)
            if isinstance(asset_key, basestring):
                asset_key = AssetKey.from_string(asset_key)
                __, asset_key = self.asset_db_key(asset_key)
            asset_key['org'] = dest_course_key.org
            asset_key['course'] = dest_course_key.course
            if getattr(dest_course_key, 'deprecated', False):  # remove the run if exists
                if 'run' in asset_key:
                    del asset_key['run']
                asset_id = asset_key
            else:  # add the run, since it's the last field, we're golden
                asset_key['run'] = dest_course_key.run
                asset_id = unicode(
                    dest_course_key.make_asset_key(asset_key['category'], asset_key['name']).for_branch(None)
                )

            self.fs.put(
                source_content.read(),
                _id=asset_id, filename=asset['filename'], content_type=asset['contentType'],
                displayname=asset['displayname'], content_son=asset_key,
                # thumbnail is not technically correct but will be functionally correct as the code
                # only looks at the name which is not course relative.
                thumbnail_location=asset['thumbnail_location'],
                # import_path=asset['import_path'],
                import_path=asset['import_path'] if 'import_path' in asset else '',
                # getattr b/c caching may mean some pickled instances don't have attr
                locked=asset.get('locked', False)
            )

    def delete_all_course_assets(self, course_key):
        """
        Delete all assets identified via this course_key. Dangerous operation which may remove assets
        referenced by other runs or other courses.
        :param course_key:
        """
        course_query = query_for_course(course_key)
        matching_assets = self.fs_files.find(course_query)
        for asset in matching_assets:
            asset_key = self.make_id_son(asset)
            self.fs.delete(asset_key)

    # codifying the original order which pymongo used for the dicts coming out of location_to_dict
    # stability of order is more important than sanity of order as any changes to order make things
    # unfindable
    ordered_key_fields = ['category', 'name', 'course', 'tag', 'org', 'revision']
    property_names = {
        'category': 'block_type',
        'name': 'block_id',
        'course': 'course',
        'tag': 'DEPRECATED_TAG',
        'org': 'org',
        'revision': 'branch',
    }

    @classmethod
    def asset_db_key(cls, location):
        """
        Returns the database _id and son structured lookup to find the given asset location.
        """
        dbkey = SON((field_name,
                     getattr(location, cls.property_names[field_name])) for field_name in cls.ordered_key_fields)
        if getattr(location, 'deprecated', False):
            content_id = dbkey
        else:
            # NOTE, there's no need to state that run doesn't exist in the negative case b/c access via
            # SON requires equivalence (same keys and values in exact same order)
            dbkey['run'] = location.run
            content_id = unicode(location.for_branch(None))
        return content_id, dbkey

    def make_id_son(self, fs_entry):
        """
        Change the _id field in fs_entry into the properly ordered SON or string
        Args:
            fs_entry: the element returned by self.fs_files.find
        """
        _id_field = fs_entry.get('_id', fs_entry)
        if isinstance(_id_field, basestring):
            return _id_field
        dbkey = SON((field_name, _id_field.get(field_name)) for field_name in self.ordered_key_fields)
        if 'run' in _id_field:
            # NOTE, there's no need to state that run doesn't exist in the negative case b/c access via
            # SON requires equivalence (same keys and values in exact same order)
            dbkey['run'] = _id_field['run']
        fs_entry['_id'] = dbkey
        return dbkey

    def ensure_indexes(self):
        # Index needed thru 'category' by `_get_all_content_for_course` and others. That query also takes a sort
        # which can be `uploadDate`, `displayname`,
        # TODO: uncomment this line once this index in prod is cleaned up. See OPS-2863 for tracking clean up.
        #  create_collection_index(
        #  self.fs_files,
        #  [
        #  ('_id.tag', pymongo.ASCENDING),
        #  ('_id.org', pymongo.ASCENDING),
        #  ('_id.course', pymongo.ASCENDING),
        #  ('_id.category', pymongo.ASCENDING)
        #  ],
        #  sparse=True,
        #  background=True
        #  )
        create_collection_index(
            self.fs_files,
            [
                ('content_son.org', pymongo.ASCENDING),
                ('content_son.course', pymongo.ASCENDING),
                ('uploadDate', pymongo.DESCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('_id.org', pymongo.ASCENDING),
                ('_id.course', pymongo.ASCENDING),
                ('_id.name', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('content_son.org', pymongo.ASCENDING),
                ('content_son.course', pymongo.ASCENDING),
                ('content_son.name', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('_id.org', pymongo.ASCENDING),
                ('_id.course', pymongo.ASCENDING),
                ('uploadDate', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('_id.org', pymongo.ASCENDING),
                ('_id.course', pymongo.ASCENDING),
                ('displayname', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('content_son.org', pymongo.ASCENDING),
                ('content_son.course', pymongo.ASCENDING),
                ('uploadDate', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )
        create_collection_index(
            self.fs_files,
            [
                ('content_son.org', pymongo.ASCENDING),
                ('content_son.course', pymongo.ASCENDING),
                ('displayname', pymongo.ASCENDING)
            ],
            sparse=True,
            background=True
        )


def query_for_course(course_key, category=None):
    """
    Construct a SON object that will query for all assets possibly limited to the given type
    (thumbnail v assets) in the course using the index in mongo_indexes.md
    """
    if getattr(course_key, 'deprecated', False):
        prefix = '_id'
    else:
        prefix = 'content_son'
    dbkey = SON([
        ('{}.tag'.format(prefix), XASSET_LOCATION_TAG),
        ('{}.org'.format(prefix), course_key.org),
        ('{}.course'.format(prefix), course_key.course),
    ])
    if category:
        dbkey['{}.category'.format(prefix)] = category
    if getattr(course_key, 'deprecated', False):
        dbkey['{}.run'.format(prefix)] = {'$exists': False}
    else:
        dbkey['{}.run'.format(prefix)] = course_key.run
    return dbkey
