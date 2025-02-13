educationalReformData <- read.csv("Downloads/EducationalReformDataCohortA.csv", header = TRUE)
#account for average 100 point increase every year
educationalReformData$ELScore16 <- educationalReformData$ELScore16 - 100
educationalReformData$MAScore16 <- educationalReformData$MAScore16 - 100
educationalReformData$ELScore17 <- educationalReformData$ELScore17 - 200
educationalReformData$MAScore17 <- educationalReformData$MAScore17 - 200
t.test(educationalReformData$ELScore17, educationalReformData$MAScore15, paired=TRUE, conf.level=0.95)
