from HanTa import HanoverTagger as ht



tagger = ht.HanoverTagger('morphmodel_ger.pgz')

print(tagger.analyze('Fachmärkte'))