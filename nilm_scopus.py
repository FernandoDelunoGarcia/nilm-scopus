import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import glob2
import datetime
import itertools

class Utils:
    def __init__(self):
        self.default_font = dict(family="Courier New, monospace", size=12, color="#7f7f7f")
        self.default_line = dict(width=1, color="blue")

        #dataset path
        self.dts_list = glob2.glob("./datasets/" + "*.csv")

        #date range
        self.min_year = 1990
        self.max_year = datetime.datetime.now().year

        self.max_papers = 100
        self.max_keywords = 100


utils = Utils()

@st.cache
def LoadDataset(filename):
    df=pd.read_csv(filename)
    return df

def getPublicationsByYear(df, from_date, to_date):
    publications = df[(df['Year']>=from_date) & (df['Year']<=to_date)]
    return publications

def EvaluatePublicationsPerYear(df):
    counts = df['Year'].value_counts()
    publications_per_year = pd.DataFrame({'Year' : counts.index, 'Count' : counts.values})
    publications_per_year = publications_per_year.sort_values(by='Year')
    return publications_per_year

def EvaluatePaperCitations(df):
    first_author = [x.split(',')[0] for x in df['Authors']]
    paper_year = [str(x) for x in df['Year']] 
    paper = ["{0}, {1}".format(author,year) for (author,year) in zip(first_author, paper_year)]
    citations_per_paper = pd.DataFrame({'Paper' : paper, 'Count' : df['Cited by'].values, 'Title' : df['Title'].values})
    citations_per_paper = citations_per_paper.sort_values(by='Count', ascending=False)
    return citations_per_paper

def EvaluateIndexKeywords(df):
    keywords = [str(x).split(';') for x in df['Index Keywords']]
    keywords_list = list(itertools.chain.from_iterable(keywords))
    keywords_list = [s.lower() for s in keywords_list]

    index_keywords = pd.DataFrame(keywords_list)
    index_keywords.columns = ['Keywords']
    index_keywords['Count'] = 1
    index_keywords = index_keywords.groupby('Keywords').count().sort_values(by='Count', ascending=False).reset_index()
    index_keywords = index_keywords.dropna(how='all')
    return index_keywords


def PlotPublicationsPerYear(publications):
    trace = go.Scatter(x = publications['Year'], y = publications['Count'], line=utils.default_line)
    fig = go.Figure(data = [trace])
    fig.update_layout(title='Publications Per Year', xaxis_title="Year", yaxis_title="Publications",font=utils.default_font)
    return fig

def PlotCitationsPerPaper(publications):
    trace = go.Bar(x = publications.index, y = publications['Count'], hovertext = publications['Title'], orientation='v')
    fig = go.Figure(data = [trace])
    xaxis=dict(tickvals=publications.index, ticktext=publications['Paper'],tickangle=45)
    fig.update_layout(title='Most Cited Papers', yaxis_title="Cited by", xaxis=xaxis, xaxis_title="Publication",font=utils.default_font)

    return fig

def PlotIndexKeywords(publications):
    trace = go.Bar(x = publications.index, y = publications['Count'], orientation='v')
    fig = go.Figure(data = [trace])
    xaxis=dict(tickvals=publications.index, ticktext=publications['Keywords'],tickangle=45)
    fig.update_layout(title='Most Popular Keywords', yaxis_title="Count", xaxis=xaxis, xaxis_title="Index Keyword",font=utils.default_font)
    return fig


if __name__ == "__main__":
    st.title("NILM Papers")

    st.sidebar.title("About")
    st.sidebar.info("This is ...")

    st.sidebar.title("Dataset")
    filename = st.sidebar.selectbox("Dataset choices", utils.dts_list, 0)

    st.sidebar.title("Date Range")
    year_to_filter = st.sidebar.slider('Year', utils.min_year, utils.max_year, utils.max_year)

    st.sidebar.title("Most Cited Papers")
    papers_to_filter = st.sidebar.slider('Papers', 1, utils.max_papers, utils.max_papers)

    st.sidebar.title("Most Popular Keywords")
    keywords_to_filter = st.sidebar.slider('Top', 1, utils.max_keywords, utils.max_keywords)



    df = LoadDataset(filename)
    publications = getPublicationsByYear(df, utils.min_year, year_to_filter)

    if publications.shape[0] > 0:
        st.write(publications)

        history = EvaluatePublicationsPerYear(publications)
        history_fig = PlotPublicationsPerYear(history)
        st.write(history_fig)

        most_cited_papers = EvaluatePaperCitations(publications)
        most_cited_papers_fig = PlotCitationsPerPaper(most_cited_papers.iloc[0:papers_to_filter])
        st.write(most_cited_papers_fig)

        index_keywords = EvaluateIndexKeywords(publications)
        index_keywords_fig = PlotIndexKeywords(index_keywords.iloc[0:keywords_to_filter])
        st.write(index_keywords_fig)
