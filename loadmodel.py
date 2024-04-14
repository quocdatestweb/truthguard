import pickle
# Tải mô hình từ file
with open('model/model.pkl', 'rb') as f:
    try:
        model = pickle.load(f)
    except (pickle.UnpicklingError, EOFError):
        print('Error loading model')