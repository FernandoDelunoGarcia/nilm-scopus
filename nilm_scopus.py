import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import glob2
import datetime
import itertools
import sys
import os

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

        self.column_authors = 'Authors'
        self.column_title = 'Title'
        self.column_year = 'Year'
        self.column_citations = 'Cited by'
        self.column_ikeywords = 'Index Keywords'
        


utils = Utils()

@st.cache
def LoadDataset(filename):
    df=pd.read_csv(filename)
    df[utils.column_citations] = df[utils.column_citations].fillna(0)
    df = df.sort_values(by=utils.column_citations, ascending=False)
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
    first_author = [x.split(',')[0] for x in df[utils.column_authors]]
    paper_year = [str(x) for x in df[utils.column_year]] 
    paper = ["{0}, {1}".format(author,year) for (author,year) in zip(first_author, paper_year)]
    citations_per_paper = pd.DataFrame({'Paper' : paper, 'Count' : df[utils.column_citations].values, 'Title' : df[utils.column_title].values})
    return citations_per_paper

def EvaluateIndexKeywords(df):
    keywords = [str(x).split(';') for x in df[utils.column_ikeywords]]
    keywords_list = list(itertools.chain.from_iterable(keywords))
    keywords_list = [s.lower() for s in keywords_list]

    index_keywords = pd.DataFrame(keywords_list)
    index_keywords.columns = ['Keywords']
    index_keywords = index_keywords.loc[index_keywords['Keywords'] != 'nan']
    index_keywords['Count'] = 1
    index_keywords = index_keywords.groupby('Keywords').count().sort_values(by='Count', ascending=False).reset_index()
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
    st.sidebar.info("A tool to investigate publications that have cited **Nonintrusive Appliance Load Monitoring**, Hart G.W. (1992).")

    st.sidebar.title("Dataset")
    filename = st.sidebar.selectbox("Dataset choices", utils.dts_list, 0)

    st.sidebar.title("Date Range")
    min_year_to_filter, max_year_to_filter = st.sidebar.slider('Year', utils.min_year, utils.max_year, (utils.min_year, utils.max_year), 1)

    st.sidebar.title("Most Cited Papers")
    papers_to_filter = st.sidebar.slider('Papers', 1, utils.max_papers, utils.max_papers)

    st.sidebar.title("Most Popular Keywords")
    keywords_to_filter = st.sidebar.slider('Top', 1, utils.max_keywords, utils.max_keywords)

    export_images_pressed = st.sidebar.button('Export Images')

    df = LoadDataset(filename)
    publications = getPublicationsByYear(df, min_year_to_filter, max_year_to_filter)

    if publications.shape[0] > 0:
    
        st.markdown("{0} documents have cited: ".format(publications.shape[0]) + "**Nonintrusive Appliance Load Monitoring**.")
    
        st.write(publications[[utils.column_authors, utils.column_year, utils.column_title, utils.column_citations]])

        history = EvaluatePublicationsPerYear(publications)
        history_fig = PlotPublicationsPerYear(history)
        st.write(history_fig)

        most_cited_papers = EvaluatePaperCitations(publications)
        most_cited_papers_fig = PlotCitationsPerPaper(most_cited_papers.iloc[0:papers_to_filter])
        st.write(most_cited_papers_fig)

        index_keywords = EvaluateIndexKeywords(publications)
        index_keywords_fig = PlotIndexKeywords(index_keywords.iloc[0:keywords_to_filter])
        st.write(index_keywords_fig)

        if export_images_pressed:
            path = './outputs/'
            if os.path.exists(path):
                suffix = str(min_year_to_filter) + '_' + str(max_year_to_filter) + ".svg"
                history_fig.write_image(path + 'publications_' + suffix)
                most_cited_papers_fig.write_image(path + 'mostcited_' + suffix)
                index_keywords_fig.write_image(path + 'topkeywords_' + suffix)
            else:
                raise "Invalid path"
