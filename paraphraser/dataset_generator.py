import numpy as np
from nlp_pipeline import nlp_pipeline
from keras.preprocessing.sequence import pad_sequences
from load_sent_embeddings import load_sentence_embeddings
from six.moves import xrange

class ParaphraseDataset(object):
    def __init__(self, path, embeddings, word_to_id):
        i = 0

        with open(path, 'r') as f:
            for line in f:
                i += 1

        self.path = path
        self.embeddings = embeddings
        self.word_to_id = word_to_id
        self.dataset_size = i
        self.vocab_size, self.embedding_size = embeddings.shape

    def load(self, start_id, end_id, unk_id, mask_id, max_encoder_tokens, max_decoder_tokens):
        i = 0
        batch_source_ids = []
        batch_ref_ids = []
        batch_target_ids = []
        batch_source_lengths = []
        batch_ref_lengths = []
        batch_target_lengths = []

        with open(self.path, 'r') as f:
            for i, line in enumerate(f):
                source, ref = line.split('\t')

                source_ids = nlp_pipeline(source, self.word_to_id, unk_id)
                ref_ids = nlp_pipeline(ref, self.word_to_id, unk_id)

                ref_ids = [start_id] + ref_ids + [end_id]
                target_ids = ref_ids[1:]

                source_len = len(source_ids)
                ref_len = len(ref_ids)
                target_len = len(target_ids)

                batch_source_ids.append(source_ids)
                batch_ref_ids.append(ref_ids)
                batch_target_ids.append(target_ids)
                batch_source_lengths.append(source_len)
                batch_ref_lengths.append(ref_len)
                batch_target_lengths.append(target_len)

                if i % 1000 == 0:
                    import datetime as dt
                    print(dt.datetime.now(), flush=True)
                    print(i)

        encoder_input_data, decoder_input_data, one_hot_decoder_target_data = self.encode_batch(
            batch_size, batch_source_ids, batch_ref_ids, batch_target_ids, mask_id, max_encoder_tokens, max_decoder_tokens)
        return ([encoder_input_data, decoder_input_data], one_hot_decoder_target_data)


    def generate_batch(self, batch_size, start_id, end_id, unk_id, mask_id, max_encoder_tokens, max_decoder_tokens):
        i = 0
        batch_source_ids = []
        batch_ref_ids = []
        batch_target_ids = []
        batch_source_lengths = []
        batch_ref_lengths = []
        batch_target_lengths = []

        with open(self.path, 'r') as f:
            for line in f:
                source, ref = line.split('\t')

                source_ids = nlp_pipeline(source, self.word_to_id, unk_id)
                ref_ids = nlp_pipeline(ref, self.word_to_id, unk_id)

                ref_ids = [start_id] + ref_ids + [end_id]
                target_ids = ref_ids[1:]

                source_len = len(source_ids)
                ref_len = len(ref_ids)
                target_len = len(target_ids)

                batch_source_ids.append(source_ids)
                batch_ref_ids.append(ref_ids)
                batch_target_ids.append(target_ids)
                batch_source_lengths.append(source_len)
                batch_ref_lengths.append(ref_len)
                batch_target_lengths.append(target_len)

                i += 1
                if i % batch_size == 0:
                    encoder_input_data, decoder_input_data, one_hot_decoder_target_data = self.encode_batch(
                        batch_size, batch_source_ids, batch_ref_ids, batch_target_ids, mask_id, max_encoder_tokens, max_decoder_tokens)
                    yield ([encoder_input_data, decoder_input_data], one_hot_decoder_target_data)

                    batch_source_ids = []
                    batch_ref_ids = []
                    batch_target_ids = []
                    batch_source_lengths = []
                    batch_ref_lengths = []
                    batch_target_lengths = []

    def encode_batch(self, batch_size, source_ids, ref_ids, target_ids, mask_id, max_encoder_tokens, max_decoder_tokens):
        encoder_input_data = np.array(pad_sequences(source_ids, maxlen=max_encoder_tokens, padding='post', value=mask_id))
        decoder_input_data = np.array(pad_sequences(ref_ids, maxlen=max_decoder_tokens, padding='post', value=mask_id))
        decoder_target_data = np.array(pad_sequences(target_ids, maxlen=max_decoder_tokens, padding='post', value=mask_id))

        one_hot_decoder_target_data = np.zeros((batch_size, max_decoder_tokens, self.vocab_size))
        for i in xrange(decoder_target_data.shape[0]):
            for j in xrange(max_decoder_tokens):
                one_hot_decoder_target_data[i, j, decoder_target_data[i][j]] = 1

        return encoder_input_data, decoder_input_data, one_hot_decoder_target_data

if __name__ == '__main__':
    import datetime as dt
    word_to_id, idx_to_word, embeddings, start_id, end_id, unk_id = load_sentence_embeddings()
    dataset = ParaphraseDataset('/media/sdb/datasets/para-nmt-5m-processed/para-nmt-5m-processed.txt', embeddings, word_to_id)
    print(dt.datetime.now(), flush=True)
    d = dataset.load(start_id, end_id, unk_id, 5800, 30, 30)
    print(dt.datetime.now(), flush=True)
    for [encoder_input_data, decoder_input_data], one_hot_decoder_target_data in d:
        print(encoder_input_data, flush=True)
        print(decoder_input_data, flush=True)
        print(one_hot_decoder_target_data, flush=True)
        break

