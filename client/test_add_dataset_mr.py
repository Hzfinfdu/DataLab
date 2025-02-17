from datalabs import load_dataset
from featurize.general import get_features_sample_level
from aggregate.text_classification import get_features_dataset_level
from dataclasses import asdict, dataclass, field
import json
from datalabs.utils.more_features import prefix_dict_key
import requests


def get_info(dataset_name:str, field = "text"):
    """
    Input:
    dataset_name: the dataset name of dataloader script, for example, mr
    field: the field to be featurized
    Output:
    asdict(dataset['train']._info): metadata information
    features_mongodb: features of metadata information
    dataset: detailed sample of all dataset splits
    """


    # load dataset
    dataset = load_dataset(dataset_name)

    # Feature
    all_splits = dataset['train']._info.splits.keys()


    features_mongodb = {}
    for split_name in all_splits:

        # add sample-level features
        features_mongodb.update(asdict(dataset[split_name]._info)["features"])

        # add dataset-level features
        dataset[split_name] = dataset[split_name].apply(get_features_dataset_level, mode="memory", prefix="avg")
        features_dataset = asdict(dataset[split_name]._info)["features_dataset"]


        for attr, feat_info in features_dataset.items():
            value = dataset[split_name]._stat[attr]
            feat_info["value"] = value
            features_dataset[attr] = feat_info

        features_dataset_new = prefix_dict_key(features_dataset, prefix=split_name)

        features_mongodb.update(features_dataset_new)



    return asdict(dataset['train']._info), features_mongodb, dataset



def get_template(
        dataset_name, transformation, version, task_categories, tasks, split, languages, sub_dataset=None,
        summary=None, homepage=None, repository=None,
        leaderboard=None, person_of_contact=None, features=None,
        speaker_demographic=None, annotator_demographic=None, speech_situation=None,
        size=None, license_=None, huggingface_link=None,
        curation_rationale=None, genre=None, quality=None,
        similar_datasets=None, popularity=None,
        creator_name=None, multilinguality=None,
        paper_info=None, prompt_infos=None, submitter_name=None, system_metadata_ids=None,
        data_typology=None, statistical_information=None

):
    if dataset_name is None or dataset_name == '':
        raise Exception("dataset_name should not be None or ''")
    if transformation is None:
        raise Exception("transformation should not be None")
    if version is None or version == '':
        raise Exception("version should not be None or ''")

    if tasks is None or (not isinstance(tasks, list)) or len(tasks) == 0:
        raise Exception(
            "tasks should not be None and this object should be list type and its length should not be zero")
    if task_categories is None or (not isinstance(task_categories, list)) or len(task_categories) == 0:
        raise Exception(
            "task_categories should not be None and this object should be list type and its length should not be zero")

    if split is None or (not isinstance(split, dict)):
        raise Exception(
            "split should not be None and this object should be dict type")

    if languages is None or (not isinstance(languages, list)) or len(languages) == 0:
        raise Exception(
            "languages should not be None and this object should be list type and its length should not be zero")

    return {
        "dataset_name": dataset_name,
        "sub_dataset": sub_dataset,
        "split": split,
        "summary": summary,
        "homepage": homepage,
        "repository": repository,
        "paper_info": paper_info,
        "leaderboard": leaderboard,
        "person_of_contact": person_of_contact,
        "tasks": tasks,
        "task_categories": task_categories,
        "language": languages,
        "features": features,
        "speaker_demographic": speaker_demographic,
        "annotator_demographic": annotator_demographic,
        "speech_situation": speech_situation,
        "size": size,
        "license": license_,
        "huggingface_link": huggingface_link,
        "curation_rationale": curation_rationale,
        "genre": genre,
        "quality": quality,
        "similar_datasets": similar_datasets,
        "creator_name": creator_name,
        "submitter_name": submitter_name,
        "multilinguality": multilinguality,
        'system_metadata_ids': system_metadata_ids,
        'popularity': popularity,
        'transformation': transformation,
        'version': version,
        'prompt_infos': prompt_infos,
        'data_typology': data_typology,
        'statistical_information': statistical_information,
        'source': 'user',
    }


def get_paper_template(year=None, venue=None, title=None,
                       author=None, url=None, bib=None,
                       ):
    return {'year': year,
            'venue': venue,
            'title': title,
            'author': author,
            'url': url,
            'bib': bib,
            }


def get_annotator_demographic_template(
        gender=None, race=None, native_language=None,
        socioeconomic_status=None, number_of_different_speakers_represented=None,
        presence_of_disordered_speech=None, training_in_linguistics=None

):
    return {
        'gender': gender,
        'race_ethnicity': race,
        'native_language': native_language,
        'socioeconomic_status': socioeconomic_status,
        'number_of_different_speakers_represented': number_of_different_speakers_represented,
        'presence_of_disordered_speech': presence_of_disordered_speech,
        'training_in_linguistics': training_in_linguistics
    }


def get_speaker_demographic_template(
        gender=None, race=None, native_language=None,
        socioeconomic_status=None, number_of_different_speakers_represented=None,
        presence_of_disordered_speech=None,

):
    return {
        'gender': gender,
        'race_ethnicity': race,
        'native_language': native_language,
        'socioeconomic_status': socioeconomic_status,
        'number_of_different_speakers_represented': number_of_different_speakers_represented,
        'presence_of_disordered_speech': presence_of_disordered_speech,

    }


def get_speech_situation_templates(time=None, place=None, modality=None, intended_audience=None):
    return {
        'time': time,
        'place': place,
        'modality': modality,
        'intended_audience': intended_audience
    }


def get_popularity_template(number_of_download=None,
                            number_of_likes=None,
                            number_of_reposts=None,
                            number_of_visits=None):
    return {
        'number_of_download': number_of_download,
        'number_of_likes': number_of_likes,
        'number_of_reposts': number_of_reposts,
        'number_of_visits': number_of_visits,
    }


def get_size_template(samples=None, storage=None):
    return {
        'sample': samples,
        'storage': storage,
    }


def get_transformation_template(type):
    return {
        'type': type
    }


def convert_metadata_to_mongo_db_type(metadata,
                                      features,
                                      dataset_name_db,
                                      transformation = get_transformation_template('origin'),
                                      version = '0.0.1',
                                      languages = ['en'],
                                      data_typology = 'textdataset'):
    summary = metadata['description']
    homepage = metadata['homepage']
    license = metadata['license']
    subset_name = metadata['sub_dataset']
    repository = metadata['repository']
    leaderboard = metadata['leaderboard']
    person_of_contact = metadata['person_of_contact']
    huggingface_link = metadata['huggingface_link']
    curation_rationale = metadata['curation_rationale']
    genre = metadata['genre']
    similar_datasets = metadata['similar_datasets']
    creator_id = metadata['creator_id']
    submitter_id = metadata['submitter_id']
    multilinguality = metadata['multilinguality']
    speaker_demographic = metadata['speaker_demographic']
    annotator_demographic = metadata['annotator_demographic']
    speech_situation = metadata['speech_situation']

    task_categories = []  #
    tasks = []  #
    for value in metadata['task_templates']:
        task_categories.append(value['task_category'])
        tasks.append(value['task'])

    split = {}  #
    for key in metadata['splits'].keys():
        split[key] = metadata['splits'][key]['num_examples']

    return get_template(
        dataset_name=dataset_name_db,
        transformation=transformation,
        version=version,
        task_categories=task_categories,
        tasks=tasks,
        split=split,
        languages=languages,
        summary=summary,
        homepage=homepage,
        license_=license,
        sub_dataset=subset_name,
        repository=repository,
        leaderboard=leaderboard,
        person_of_contact=person_of_contact,
        huggingface_link=huggingface_link,
        curation_rationale=curation_rationale,
        genre=genre,
        similar_datasets=similar_datasets,
        creator_name=creator_id,
        submitter_name=submitter_id,
        multilinguality=multilinguality,
        speaker_demographic=speaker_demographic,
        annotator_demographic=annotator_demographic,
        speech_situation=speech_situation,
        features=features,
        data_typology=data_typology,
    )


if __name__ == "__main__":
    dataset_name_sdk = "../datasets/mr"
    version = 'origin'
    dataset_name_db = 'mr_upload_by_pf5'
    languages = ['en']


    metadata, metadata_features, dataset = get_info(dataset_name_sdk, field="text")
    store_metadata = convert_metadata_to_mongo_db_type(metadata = metadata,
                                                       features = metadata_features,
                                                       dataset_name_db = dataset_name_db,
                                                       # transformation= transformation,
                                                       # version = version,
                                                       languages = languages,)

    store_samples = []
    for split in dataset.keys():
        for sample in dataset[split]:
            store_samples.append({
                'split_name': split,
                'features': sample
            })

    store_dataset = {
        'metadata': store_metadata,
        'samples': store_samples
    }

    path = 'http://3.23.213.76:5001/upload_new_dataset'
    r = requests.post(path, json=store_dataset)
    print(r.text)
