# -*- coding: utf-8 -*-
"""SocialMediaTrollDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TqTZrEZX5JmaJzjSaIU__HuuXvG13JdN
"""

pip install transformers

import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer, TFDistilBertForSequenceClassification
import tensorflow as tf
import re
import numpy as np

df=pd.read_json('Dataset for Detection of Cyber-Trolls.json',lines=True)

df.head()

df.drop('extras',axis=1,inplace=True)

df.head()

df.rename(columns={'annotation': 'label'},inplace=True)

df.head()

type({'notes': '', 'label': ['1']})

df['label'] = df['label'].apply(lambda x: int(x['label'][0]))

df.head()

df.tail()

df.isna().sum()

total_Trolls=df['label'].sum()

total_Trolls

df.shape

no_trolls=20001-7822

import re
import nltk

url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\\S+'
def remove_urls(text):
    return re.sub(url_pattern, '', text)

df['content']=df['content'].apply(remove_urls)

X=list(df['content'])

y=list(df['label'])

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.20,random_state=0)

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = TFDistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

X_train_encoded = tokenizer(X_train, truncation=True, padding=True)
X_test_encoded = tokenizer(X_test, truncation=True, padding=True)

train_dataset = tf.data.Dataset.from_tensor_slices((dict(X_train_encoded), y_train))
test_dataset = tf.data.Dataset.from_tensor_slices((dict(X_test_encoded), y_test))

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=2e-6),
    metrics=['accuracy']  )

history = model.fit(
    train_dataset.batch(8),
    validation_data=test_dataset.batch(16),
    epochs=3,
    verbose=1
)

evaluation = model.evaluate(test_dataset.batch(32))
print("Evaluation Loss:", evaluation[0])
print("Evaluation Accuracy:", evaluation[1])

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
conf_matrix = confusion_matrix(y_true, y_pred_labels)
plt.figure(figsize=(5, 3))
sns.set(font_scale=1.4)
sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues', cbar=False,
            xticklabels=['Not a troll', 'Troll'], yticklabels=['Not a troll', 'Troll'])
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

from sklearn.metrics import classification_report
y_pred_logits = model.predict(test_dataset.batch(32))
y_pred = tf.nn.softmax(y_pred_logits.logits, axis=-1)[:, 1]
y_pred_labels = [1 if prob >= 0.5 else 0 for prob in y_pred]
y_true = y_test
report = classification_report(y_true, y_pred_labels, target_names=['Not a troll', 'Troll'])

print(report)

model.save("my_distilbert_model")

new_texts = ["You really don't know how to put your view in a good way.", "Fucking nerd", " You Pathetic loser"]


new_texts_encoded = tokenizer(new_texts, truncation=True, padding=True, return_tensors='tf')


probabilities = model(new_texts_encoded)

troll_probabilities = probabilities.logits


binary_predictions = [1 if prob[0] >= 0.5 else 0 for prob in troll_probabilities]


for text, label in zip(new_texts, binary_predictions):
    if label == 0:
        print(f"Text: {text}\nLabel: Not a troll\n")
    else:
        print(f"Text: {text}\nLabel: Troll\n")