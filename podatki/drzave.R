library(rvest)
library(dplyr)

theurl <- "https://countrycode.org/"
url <- "https://sl.wikipedia.org/wiki/Seznam_mednarodnih_klicnih_kod"

stran <- html_session(theurl) %>% read_html()

tabela <- stran %>% html_nodes(xpath = "//table")%>% .[[1]] %>% html_table(dec = ",")%>%
  rename(drzava = "COUNTRY", koda = "COUNTRY CODE")%>%dplyr::select(drzava, koda)

write.csv2(tabela, file= "Drzava")
