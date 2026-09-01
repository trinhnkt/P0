%%
%% This is file `jedm.cls', a JEDM document class that inherits from 'article.cls'
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{jedm}[2013/09/10 v1.0 JEDM class]

% Inherit all base article definitions and options
\LoadClassWithOptions{article}

% Set fonts and page layout according to JEDM guidelines
\RequirePackage{times}
\RequirePackage[left=2.75cm,right=2.75cm,top=2.25cm,bottom=2.25cm]{geometry}

% Redefine maketitle for JEDM format (sans-serif title, center authors)
\renewcommand\maketitle{\par
  \begingroup
    \renewcommand\thefootnote{\@fnsymbol\c@footnote}%
    \def\@makefnmark{\rlap{\@textsuperscript{\normalfont\@thefnmark}}}%
    \long\def\@makefntext##1{\parindent 1em\noindent
            \hb@xt@1.8em{%
                \hss\@textsuperscript{\normalfont\@thefnmark}}##1}%
    \if@twocolumn
      \ifnum \col@number=\@ne
        \@maketitle
      \else
        \twocolumn[\@maketitle]%
      \fi
    \else
      \newpage
      \global\@topnum\z@   % Prevents figures from going at top of page.
      \@maketitle
    \fi
    \thispagestyle{plain}%
    \@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\@maketitle\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}

\def\@maketitle{%
  \newpage
  \null
  \vskip 2em%
  \begin{center}%
  \let\footnote\thanks
    {\LARGE\sf\bfseries \@title \par}%
    \vskip 1.5em%
    {\large
      \lineskip .5em%
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
    \vskip 1em%
    {\large \@date}%
  \end{center}%
  \par
  \vskip 1.5em}

% Redefine abstract for JEDM (centered bold sans-serif title)
\renewenvironment{abstract}{%
      \if@twocolumn
        \section*{Abstract}%
      \else
        \small
        \begin{center}%
          {\bfseries\sffamily Abstract\vspace{-.5em}\vspace{\z@}}%
        \end{center}%
        \quotation
      \fi}
      {\if@twocolumn\else\endquotation\fi}

\endinput
