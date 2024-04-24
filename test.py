import unittest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer, OneHotEncoder
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

class SparkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.master("local[2]").appName("UnitTesting").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_pipeline_model(self):
        # Definir el esquema con los tipos correctos
        schema = StructType([
            StructField("Adicional", StringType(), True),
            StructField("Area", IntegerType(), True),
            StructField("Bedrooms", IntegerType(), True),
            StructField("Price", DoubleType(), True)  # Asegurar que Price es de tipo Double
        ])
        
        # Crear datos de prueba con el esquema definido
        data = [("house1", 2000, 3, 450000.0), ("house2", 1500, 4, 350000.0), ("house3", 1800, 3, 475000.0)]
        df = self.spark.createDataFrame(data, schema=schema)
        
        # Definir las transformaciones y el modelo
        indexer = StringIndexer(inputCol="Adicional", outputCol="AdicionalIndex")
        assembler = VectorAssembler(inputCols=["Area", "Bedrooms", "AdicionalIndex"], outputCol="features")
        scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures")
        lr = LinearRegression(featuresCol="scaledFeatures", labelCol="Price")

        # Configurar el pipeline
        pipeline = Pipeline(stages=[indexer, assembler, scaler, lr])

        # Fit y transformar
        model = pipeline.fit(df)
        result = model.transform(df)

        # Evaluar el modelo
        evaluator = RegressionEvaluator(labelCol="Price", predictionCol="prediction", metricName="rmse")
        rmse = evaluator.evaluate(result)
        self.assertLess(rmse, 100000, "El RMSE debería ser menor de 100000")

if __name__ == "__main__":
    unittest.main()