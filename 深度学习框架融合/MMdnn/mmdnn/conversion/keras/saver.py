def save_model(MainModel, network_filepath, weight_filepath, dump_filepath):
    model = MainModel.KitModel(weight_filepath)
    model.save(dump_filepath)
    print('Keras model file is saved as [{}], generated by [{}.py] and [{}].'.format(
        dump_filepath, network_filepath, weight_filepath))
