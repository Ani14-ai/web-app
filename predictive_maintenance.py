import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
df=pd.read_csv("C:\\Users\chatt\Desktop\internship\predictive_maintenance_dataset.csv")
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
X = df.iloc[:, 3:]
Y = df.iloc[:, 2]
sm=SMOTE(random_state=42)
X,Y =sm.fit_resample(X,Y)
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.3,random_state=42)
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
clf = RandomForestClassifier(n_estimators=50, max_features='auto')
clf= clf.fit(X,Y)
features = pd.DataFrame()
features['feature']= X.columns
features['important']=clf.feature_importances_
features.sort_values(by=['important'], ascending=False,inplace=True)
features.set_index('feature', inplace=True)
features.iloc[:20,:].plot(kind='barh', figsize=(30,30))
plt.show()
model = SelectFromModel(clf,prefit=True)
X_reduced = model.transform(X)
X_reduced=pd.DataFrame(X_reduced)
X_reduced.head()
#logistic regression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
log = LogisticRegression(solver='newton-cg')
log.fit(X_train, Y_train)
predictions = log.predict(X_test)
print(accuracy_score(Y_test, predictions))

from sklearn.svm import SVC
clf1=SVC(C=.1,kernel='linear',gamma=1)
clf1.fit(X_train,Y_train)
Y_pred=clf1.predict(X_test)
print(Y_pred)
print(accuracy_score(Y_test,Y_pred))