R graphing


row <- df[[25]]; plot(row$time,row$pos,type='l',ylim=rev(c(1,50)),xlim=c(0,5000))
for(i in 2:length(df)) {
    row <- df[[i]]
    lines(row$time,row$pos,type='l',ylim=rev(c(1,50)),xlim=c(0,600))
}